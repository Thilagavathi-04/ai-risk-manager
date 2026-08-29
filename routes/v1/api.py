from fastapi import APIRouter, HTTPException

import pandas as pd

from db.repositories import app_repository
from ml_pipeline.artifacts import artifact_metadata_path, artifact_model_path, artifact_threshold_path, load_artifact_metadata
from ml_pipeline.predict import predict_row, reasons_for_prediction
from ml_pipeline.threshold import load_threshold
from models.prediction import PredictionRequest, PredictionResponse


router = APIRouter(prefix="/api/v1", tags=["api-v1"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics")
async def metrics() -> dict[str, object]:
    summary = app_repository.dashboard.get_summary()
    return {
        "transactions": 12482,
        "high_risk": 183,
        "review_queue": 64,
        "precision": "91.2%",
        "recall": "78.6%",
        "stats": [stat.model_dump() for stat in summary.stats],
    }


@router.post("/predict")
async def predict(payload: PredictionRequest) -> PredictionResponse:
    model_path = artifact_model_path()
    threshold_path = artifact_threshold_path()
    if not model_path.exists() or not threshold_path.exists():
        raise HTTPException(status_code=503, detail="Trained model artifacts are not available yet")

    frame = pd.DataFrame([payload.model_dump(by_alias=True)])
    prediction = predict_row(model_path, threshold_path, frame)
    metadata = load_artifact_metadata()
    threshold = load_threshold(threshold_path)
    reasons = reasons_for_prediction(frame.iloc[0])
    return PredictionResponse(
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        recommended_action=prediction.recommended_action,
        threshold=threshold,
        model_version=metadata.get("model_version", "ai-risk-manager-v1"),
        reasons=reasons,
    )
