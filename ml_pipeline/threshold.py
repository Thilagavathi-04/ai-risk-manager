from __future__ import annotations

import json
from pathlib import Path


def save_threshold(path: Path, threshold: float) -> None:
    path.write_text(json.dumps({"threshold": threshold}, indent=2) + "\n", encoding="utf-8")


def load_threshold(path: Path) -> float:
    return float(json.loads(path.read_text(encoding="utf-8"))["threshold"])


def load_threshold_from_artifacts() -> float:
    from ml_pipeline.artifacts import artifact_threshold_path

    return load_threshold(artifact_threshold_path())
