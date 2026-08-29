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
        return {"model_version": "ai-risk-manager-v1"}
    return json.loads(metadata_path.read_text(encoding="utf-8"))
