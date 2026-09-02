from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.pipeline import Pipeline

from logging_config import configure_logging
from ml_pipeline.artifacts import artifact_metadata_path
from ml_pipeline.data_ingestion import load_raw_data
from ml_pipeline.data_validation import validate_dataset
from ml_pipeline.features import add_target, feature_columns, temporal_split
from ml_pipeline.model_zoo import (
    CandidateResult,
    build_candidate_model,
    build_model_specs,
    calibrate_isolation_forest,
    evaluate_predictions,
    leaderboard_row,
    predict_positive_probabilities,
    select_threshold,
)
from ml_pipeline.preprocessing import build_preprocessor
from paths import ARTIFACTS_DIR

logger = configure_logging()

MAX_TRAIN_ROWS = 250_000


@dataclass(frozen=True)
class TrainingArtifacts:
    baseline_path: Path
    model_path: Path
    threshold_path: Path
    leaderboard_path: Path


def build_feature_frame(raw_frame: pd.DataFrame) -> pd.DataFrame:
    validated = raw_frame.copy()
    validate_dataset(validated)
    return add_target(validated)


def train_models(frame: pd.DataFrame, model_dir: Path) -> TrainingArtifacts:
    logger.info("Starting training workflow with %s rows", len(frame))
    split = temporal_split(frame)
    train_frame = split.train
    validation_frame = split.validation
    test_frame = split.test

    features = feature_columns(frame)
    categorical_columns = [column for column in features if frame[column].dtype == "object"]
    numeric_columns = [column for column in features if column not in categorical_columns]
    logger.info(
        "Selected %s numeric features and %s categorical features",
        len(numeric_columns),
        len(categorical_columns),
    )
    X_train = train_frame[features]
    X_validation = validation_frame[features]
    X_test = test_frame[features]
    y_train = train_frame["label"]
    y_validation = validation_frame["label"]
    y_test = test_frame["label"]

    results: list[CandidateResult] = []
    model_runs: dict[str, Pipeline] = {}

    if len(X_train) > MAX_TRAIN_ROWS:
        logger.info("Capping training rows from %s to %s for practical sweep time", len(X_train), MAX_TRAIN_ROWS)
        X_train = X_train.head(MAX_TRAIN_ROWS)
        y_train = y_train.head(MAX_TRAIN_ROWS)

    for spec in build_model_specs():
        logger.info("Training %s (%s)", spec.model_name, spec.model_family)
        model = build_candidate_model(spec, y_train)
        preprocessor = build_preprocessor(numeric_columns, categorical_columns)
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        with mlflow.start_run(run_name=spec.model_name.lower().replace(" ", "_"), nested=True) as child_run:
            mlflow.log_params(
                {
                    "model_name": spec.model_name,
                    "model_family": spec.model_family,
                    "train_rows": len(X_train),
                    "validation_rows": len(X_validation),
                    "test_rows": len(X_test),
                }
            )

            pipeline.fit(X_train, y_train)
            fitted_model = pipeline.named_steps["model"]
            calibrate_isolation_forest(
                fitted_model,
                pipeline.named_steps["preprocessor"].transform(X_validation),
            )

            validation_probabilities = predict_positive_probabilities(pipeline, X_validation)
            threshold, _ = select_threshold(y_validation, validation_probabilities)
            validation_metrics = evaluate_predictions(y_validation, validation_probabilities, threshold)

            test_probabilities = predict_positive_probabilities(pipeline, X_test)
            test_metrics = evaluate_predictions(y_test, test_probabilities, threshold)

            artifact_path = model_dir / f"{spec.model_name.lower().replace(' ', '_')}.joblib"
            model_dir.mkdir(parents=True, exist_ok=True)
            joblib.dump(pipeline, artifact_path)
            mlflow.log_artifact(str(artifact_path))
            mlflow.log_metrics(
                {
                    "validation_precision": validation_metrics.precision,
                    "validation_recall": validation_metrics.recall,
                    "validation_f1": validation_metrics.f1,
                    "validation_pr_auc": validation_metrics.pr_auc,
                    "validation_roc_auc": validation_metrics.roc_auc,
                    "validation_expected_cost": validation_metrics.expected_cost,
                    "test_precision": test_metrics.precision,
                    "test_recall": test_metrics.recall,
                    "test_f1": test_metrics.f1,
                    "test_pr_auc": test_metrics.pr_auc,
                    "test_roc_auc": test_metrics.roc_auc,
                    "test_expected_cost": test_metrics.expected_cost,
                }
            )
            mlflow.log_dict(
                {
                    "model_name": spec.model_name,
                    "model_family": spec.model_family,
                    "threshold": round(threshold, 6),
                    "validation": validation_metrics.__dict__,
                    "test": test_metrics.__dict__,
                    "mlflow_run_id": child_run.info.run_id,
                    "mlflow_run_name": child_run.info.run_name,
                },
                artifact_file=f"{spec.model_name.lower().replace(' ', '_')}_metrics.json",
            )
            mlflow.sklearn.log_model(pipeline, artifact_path="model")

            result = CandidateResult(
                model_name=spec.model_name,
                model_family=spec.model_family,
                threshold=threshold,
                validation=validation_metrics,
                test=test_metrics,
                mlflow_run_id=child_run.info.run_id,
                mlflow_run_name=child_run.info.run_name,
                artifact_path=str(artifact_path),
            )
            results.append(result)
            model_runs[spec.model_name] = pipeline
            logger.info(
                "%s validation PR-AUC=%.4f test PR-AUC=%.4f expected_cost=%.2f",
                spec.model_name,
                validation_metrics.pr_auc,
                test_metrics.pr_auc,
                test_metrics.expected_cost,
            )

    if not results:
        raise RuntimeError("No candidate models were trained")

    selected_result = max(results, key=lambda result: (result.validation.pr_auc, -result.validation.expected_cost))
    selected_pipeline = model_runs[selected_result.model_name]

    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "risk_model.joblib"
    threshold_path = model_dir / "threshold.json"
    leaderboard_path = model_dir / "model_leaderboard.json"

    leaderboard = [
        {**leaderboard_row(result), "is_selected": result.model_name == selected_result.model_name}
        for result in results
    ]

    metadata = {
        "model_version": "ai-risk-manager-v2",
        "experiment": "ai-risk-manager-paysim1",
        "run_name": "train_pipeline",
        "selected_model_name": selected_result.model_name,
        "selected_model_family": selected_result.model_family,
        "selected_run_id": selected_result.mlflow_run_id,
        "selected_run_name": selected_result.mlflow_run_name,
        "selected_threshold": round(selected_result.threshold, 6),
        "selected_artifact_path": str(model_path),
        "selected_model_source_artifact": selected_result.artifact_path,
        "training_row_cap": MAX_TRAIN_ROWS,
        "sklearn_version": "1.9.0",
        "status": "completed",
        "user": "spidey",
        "training_summary": (
            f"Selected {selected_result.model_name} from a ten-model MLflow sweep using a shared temporal split. "
            "The winner was chosen by validation PR-AUC with expected cost as the tie-breaker."
        ),
        "artifact_uri": str(model_dir),
        "model_leaderboard": leaderboard,
    }

    mlflow.log_params(
        {
            "selected_model_name": selected_result.model_name,
            "selected_model_family": selected_result.model_family,
            "selected_run_id": selected_result.mlflow_run_id,
            "selected_run_name": selected_result.mlflow_run_name,
            "training_row_cap": MAX_TRAIN_ROWS,
        }
    )
    mlflow.log_metrics(
        {
            "selected_validation_precision": selected_result.validation.precision,
            "selected_validation_recall": selected_result.validation.recall,
            "selected_validation_f1": selected_result.validation.f1,
            "selected_validation_pr_auc": selected_result.validation.pr_auc,
            "selected_validation_roc_auc": selected_result.validation.roc_auc,
            "selected_validation_expected_cost": selected_result.validation.expected_cost,
            "selected_test_precision": selected_result.test.precision,
            "selected_test_recall": selected_result.test.recall,
            "selected_test_f1": selected_result.test.f1,
            "selected_test_pr_auc": selected_result.test.pr_auc,
            "selected_test_roc_auc": selected_result.test.roc_auc,
            "selected_test_expected_cost": selected_result.test.expected_cost,
        }
    )

    logger.info("Saving model and threshold artifacts to %s", model_dir)
    joblib.dump(selected_pipeline, model_path)
    threshold_path.write_text(json.dumps({"threshold": selected_result.threshold}, indent=2) + "\n", encoding="utf-8")
    artifact_metadata_path().write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    leaderboard_path.write_text(json.dumps(leaderboard, indent=2) + "\n", encoding="utf-8")
    mlflow.log_artifact(str(model_path))
    mlflow.log_artifact(str(threshold_path))
    mlflow.log_artifact(str(artifact_metadata_path()))
    mlflow.log_artifact(str(leaderboard_path))
    mlflow.sklearn.log_model(selected_pipeline, artifact_path="model")
    logger.info("Artifacts saved and MLflow model logged for %s", selected_result.model_name)
    return TrainingArtifacts(
        baseline_path=model_path,
        model_path=model_path,
        threshold_path=threshold_path,
        leaderboard_path=leaderboard_path,
    )


def main() -> None:
    logger.info("Starting AI Risk Manager training pipeline")
    mlflow.set_experiment("ai-risk-manager-paysim1")
    with mlflow.start_run(run_name="train_pipeline"):
        logger.info("Loading raw dataset")
        raw_frame = load_raw_data()
        frame = build_feature_frame(raw_frame)
        logger.info("Dataset validated and target added")
        train_models(frame, ARTIFACTS_DIR)
    logger.info("AI Risk Manager training pipeline completed")


if __name__ == "__main__":
    main()
