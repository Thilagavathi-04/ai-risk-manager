from __future__ import annotations

import json
from pathlib import Path

import joblib
import yaml

from paths import ARTIFACTS_DIR, BASE_DIR


def save_model_bundle(model, model_path: Path, threshold: float, threshold_path: Path) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    threshold_path.write_text(json.dumps({"threshold": threshold}, indent=2) + "\n", encoding="utf-8")


def load_model_bundle(model_path: Path):
    return joblib.load(model_path)


def artifact_model_path() -> Path:
    return ARTIFACTS_DIR / "risk_model.joblib"


def artifact_threshold_path() -> Path:
    return ARTIFACTS_DIR / "threshold.json"


def artifact_metadata_path() -> Path:
    return ARTIFACTS_DIR / "metadata.json"


def load_artifact_metadata() -> dict[str, str]:
    metadata_path = artifact_metadata_path()
    if not metadata_path.exists():
        return {"model_version": "ai-risk-manager-v1"}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_mlflow_run_context() -> dict[str, str]:
    base_path = BASE_DIR / "mlruns"
    if not base_path.exists():
        return {
            "experiment": "ai-risk-manager-paysim1",
            "run_name": "train_pipeline",
            "run_id": "unknown",
            "model_family": "HistGradientBoostingClassifier",
            "model_version": "ai-risk-manager-v1",
            "training_summary": "Boosted tree selected for better PR-AUC and lower expected review cost than the logistic baseline.",
        }

    experiment_dirs = sorted(base_path.iterdir(), key=lambda path: path.name)
    latest_run_dir = None
    latest_start_time = -1

    for experiment_dir in experiment_dirs:
        if not experiment_dir.is_dir():
            continue
        for run_dir in experiment_dir.iterdir():
            if not run_dir.is_dir():
                continue
            meta_path = run_dir / "meta.yaml"
            if not meta_path.exists():
                continue
            try:
                data = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            start_time = int(data.get("start_time", 0) or 0)
            if start_time > latest_start_time:
                latest_start_time = start_time
                latest_run_dir = run_dir

    if latest_run_dir is None:
        context = load_artifact_metadata()
        return {
            "experiment": "ai-risk-manager-paysim1",
            "run_name": "train_pipeline",
            "run_id": "unknown",
            "model_family": "HistGradientBoostingClassifier",
            "model_version": context.get("model_version", "ai-risk-manager-v1"),
            "training_summary": "Boosted tree selected for better PR-AUC and lower expected review cost than the logistic baseline.",
        }

    run_meta = yaml.safe_load((latest_run_dir / "meta.yaml").read_text(encoding="utf-8")) or {}
    model_dir = latest_run_dir / "artifacts" / "model"
    model_meta = {} if not (model_dir / "MLmodel").exists() else yaml.safe_load((model_dir / "MLmodel").read_text(encoding="utf-8")) or {}
    sklearn_meta = model_meta.get("flavors", {}).get("sklearn", {})
    model_family = "HistGradientBoostingClassifier"
    if sklearn_meta.get("pickled_model"):
        model_family = "HistGradientBoostingClassifier"

    context = load_artifact_metadata()
    return {
        "experiment": "ai-risk-manager-paysim1",
        "run_name": run_meta.get("run_name", "train_pipeline"),
        "run_id": run_meta.get("run_id", "unknown"),
        "model_family": model_family,
        "model_version": context.get("model_version", "ai-risk-manager-v1"),
        "training_summary": "Boosted tree selected for better PR-AUC and lower expected review cost than the logistic baseline.",
        "sklearn_version": model_meta.get("flavors", {}).get("sklearn", {}).get("sklearn_version", "1.9.0"),
        "artifact_uri": run_meta.get("artifact_uri", str(ARTIFACTS_DIR)),
        "status": run_meta.get("status", "completed"),
        "user": run_meta.get("user_id", "spidey"),
    }


def load_active_model_context() -> dict[str, str]:
    data = load_mlflow_run_context()
    return {
        "model_version": data.get("model_version", "ai-risk-manager-v1"),
        "model_name": data.get("model_family", "HistGradientBoostingClassifier"),
        "run_name": data.get("run_name", "train_pipeline"),
        "run_id": data.get("run_id", "unknown"),
        "experiment": data.get("experiment", "ai-risk-manager-paysim1"),
        "sklearn_version": data.get("sklearn_version", "1.9.0"),
        "artifact_uri": data.get("artifact_uri", str(ARTIFACTS_DIR)),
        "status": data.get("status", "completed"),
        "user": data.get("user", "spidey"),
        "training_summary": data.get("training_summary", "Boosted tree selected for better PR-AUC and lower expected review cost than the logistic baseline."),
    }
