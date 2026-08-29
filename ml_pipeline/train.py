from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from logging_config import configure_logging
from ml_pipeline.data_ingestion import load_raw_data
from ml_pipeline.data_validation import validate_dataset
from ml_pipeline.artifacts import artifact_metadata_path
from ml_pipeline.features import add_target, feature_columns, temporal_split
from ml_pipeline.preprocessing import build_preprocessor
from paths import ARTIFACTS_DIR

logger = configure_logging()


@dataclass(frozen=True)
class TrainingArtifacts:
    baseline_path: Path
    model_path: Path
    threshold_path: Path


def build_feature_frame(raw_frame: pd.DataFrame) -> pd.DataFrame:
    validated = raw_frame.copy()
    validate_dataset(validated)
    return add_target(validated)


def train_models(frame: pd.DataFrame, model_dir: Path) -> TrainingArtifacts:
    logger.info("Starting training workflow with %s rows", len(frame))
    split = temporal_split(frame)
    train_frame = split.train
    validation_frame = split.validation

    features = feature_columns(frame)
    categorical_columns = [column for column in features if frame[column].dtype == "object"]
    numeric_columns = [column for column in features if column not in categorical_columns]
    logger.info("Selected %s numeric features and %s categorical features", len(numeric_columns), len(categorical_columns))
    preprocessor = build_preprocessor(numeric_columns, categorical_columns)

    X_train = train_frame[features]
    y_train = train_frame["label"]

    baseline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    logger.info("Training baseline logistic regression model")
    baseline.fit(X_train, y_train)

    boosted = Pipeline([
        ("preprocessor", preprocessor),
        ("model", HistGradientBoostingClassifier(max_depth=6, learning_rate=0.08, max_iter=150)),
    ])
    logger.info("Training boosted tree model")
    boosted.fit(X_train, y_train)

    model_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = model_dir / "baseline_model.joblib"
    model_path = model_dir / "risk_model.joblib"
    threshold_path = model_dir / "threshold.json"
    logger.info("Saving model and threshold artifacts to %s", model_dir)
    joblib.dump(baseline, baseline_path)
    joblib.dump(boosted, model_path)
    threshold_path.write_text('{"threshold": 0.72}\n', encoding="utf-8")
    artifact_metadata_path().write_text('{"model_version": "ai-risk-manager-v1"}\n', encoding="utf-8")
    mlflow.log_artifact(str(model_path))
    mlflow.log_artifact(str(threshold_path))
    mlflow.log_artifact(str(artifact_metadata_path()))
    mlflow.sklearn.log_model(boosted, artifact_path="model")
    logger.info("Artifacts saved and MLflow model logged")
    _ = validation_frame
    return TrainingArtifacts(baseline_path=baseline_path, model_path=model_path, threshold_path=threshold_path)


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
