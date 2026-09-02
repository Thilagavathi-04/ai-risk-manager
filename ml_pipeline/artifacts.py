from __future__ import annotations

import json
from pathlib import Path

import joblib

from paths import ARTIFACTS_DIR


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
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_mlflow_run_context() -> dict[str, object]:
    return load_artifact_metadata()


def load_active_model_context() -> dict[str, object]:
    data = load_mlflow_run_context()
    return {
        "model_version": data.get("model_version"),
        "model_name": data.get("selected_model_name") or data.get("model_family"),
        "model_family": data.get("selected_model_family") or data.get("model_family"),
        "run_name": data.get("selected_run_name") or data.get("run_name"),
        "run_id": data.get("selected_run_id") or data.get("run_id"),
        "experiment": data.get("experiment"),
        "sklearn_version": data.get("sklearn_version"),
        "artifact_uri": data.get("artifact_uri"),
        "status": data.get("status"),
        "user": data.get("user"),
        "training_summary": data.get("training_summary"),
        "selected_threshold": data.get("selected_threshold"),
        "selected_artifact_path": data.get("selected_artifact_path"),
        "model_leaderboard": data.get("model_leaderboard", []),
    }
