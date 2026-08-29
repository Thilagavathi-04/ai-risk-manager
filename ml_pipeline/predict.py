from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_pipeline.artifacts import load_model_bundle
from ml_pipeline.threshold import load_threshold


@dataclass(frozen=True)
class PredictionResult:
    risk_score: float
    risk_level: str
    recommended_action: str


def predict_row(model_path: Path, threshold_path: Path, features: pd.DataFrame) -> PredictionResult:
    model = load_model_bundle(model_path)
    threshold = load_threshold(threshold_path)
    risk_score = float(model.predict_proba(features)[:, 1][0])
    if risk_score >= threshold:
        risk_level = "HIGH"
        recommended_action = "Manual Review"
    elif risk_score >= threshold * 0.5:
        risk_level = "MEDIUM"
        recommended_action = "Verification"
    else:
        risk_level = "LOW"
        recommended_action = "Approve"
    return PredictionResult(risk_score=risk_score, risk_level=risk_level, recommended_action=recommended_action)


def reasons_for_prediction(feature_row: pd.Series) -> list[str]:
    reasons = []
    if feature_row.get("amount", 0) > 5000:
        reasons.append("Transaction amount is unusually high")
    if feature_row.get("newbalanceOrig", 0) < feature_row.get("oldbalanceOrg", 0):
        reasons.append("Origin balance drops after the transaction")
    if feature_row.get("newbalanceDest", 0) > feature_row.get("oldbalanceDest", 0) * 3:
        reasons.append("Destination balance changes sharply")
    return reasons or ["Model found the transaction risk elevated based on learned patterns"]
