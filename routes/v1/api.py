from fastapi import APIRouter, Form, HTTPException, UploadFile
from pydantic import BaseModel
import pandas as pd

from db.repositories import app_repository
from ml_pipeline.artifacts import (
    artifact_model_path,
    artifact_threshold_path,
    load_active_model_context,
    load_artifact_metadata,
    load_model_bundle,
)
from ml_pipeline.data_validation import validate_dataset
from ml_pipeline.features import feature_columns
from ml_pipeline.predict import predict_row, reasons_for_prediction
from ml_pipeline.threshold import load_threshold
from models.prediction import PredictionRequest, PredictionResponse


router = APIRouter(prefix="/api/v1", tags=["api-v1"])


class ReviewOutcomePayload(BaseModel):
    reviewer_outcome: str


class ModelTestPayload(BaseModel):
    step: int
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dashboard")
async def dashboard_data() -> dict[str, object]:
    summary = app_repository.dashboard.get_summary()
    return summary.model_dump()


@router.get("/transactions")
async def list_transactions() -> list[dict[str, object]]:
    transactions = app_repository.list_transactions()
    return [tx.model_dump() for tx in transactions]


@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str) -> dict[str, object]:
    detail = app_repository.get_transaction(transaction_id)
    return detail.model_dump()


@router.get("/reviews")
async def list_reviews() -> list[dict[str, object]]:
    reviews = app_repository.list_reviews()
    return [review.model_dump() for review in reviews]


@router.post("/reviews/{transaction_id}")
async def record_review(transaction_id: str, payload: ReviewOutcomePayload) -> dict[str, object]:
    app_repository.record_review(transaction_id, payload.reviewer_outcome)
    detail = app_repository.get_transaction(transaction_id)
    return detail.model_dump()


@router.get("/evaluation")
async def evaluation_data() -> dict[str, object]:
    return {
        "metrics": [m.model_dump() for m in app_repository.evaluation_metrics()],
        "threshold_cost_points": [t.model_dump() for t in app_repository.threshold_cost_points()],
        "model_comparison": [mc.model_dump() for mc in app_repository.model_comparison()],
        "confusion_matrix": app_repository.confusion_matrix(),
        "selected_threshold": "0.72",
    }


@router.get("/audit")
async def audit_data() -> list[dict[str, object]]:
    entries = app_repository.audit_entries()
    return [entry.model_dump() for entry in entries]


@router.get("/settings")
async def settings_data() -> dict[str, object]:
    sections = app_repository.settings()
    return {
        "sections": [s.model_dump() for s in sections],
        "model_context": load_active_model_context(),
    }


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


@router.post("/settings/test-data")
async def validate_test_data_api(file: UploadFile) -> dict[str, object]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        first_chunk = pd.read_csv(file.file, nrows=1000)
        validate_dataset(first_chunk)

        file.file.seek(0)
        total_rows = 0
        total_fraud = 0
        columns = list(first_chunk.columns)
        has_fraud_col = "isFraud" in columns

        for chunk in pd.read_csv(
            file.file,
            chunksize=100000,
            usecols=["isFraud", "amount", "type"] if has_fraud_col else ["amount", "type"],
        ):
            total_rows += len(chunk)
            if has_fraud_col:
                total_fraud += int(chunk["isFraud"].sum())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"CSV validation failed: {exc}") from exc

    fraud_rate = (total_fraud / total_rows * 100) if total_rows > 0 else 0.0

    try:
        model_path = artifact_model_path()
        threshold_path = artifact_threshold_path()
        if model_path.exists() and threshold_path.exists():
            model = load_model_bundle(model_path)
            threshold = load_threshold(threshold_path)
            feats = feature_columns(first_chunk)

            if "isFraud" in first_chunk.columns and (first_chunk["isFraud"] == 1).any():
                candidates = first_chunk[first_chunk["isFraud"] == 1].head(20)
            elif "type" in first_chunk.columns:
                mask = first_chunk["type"].astype(str).str.upper().isin(["TRANSFER", "CASH_OUT"])
                candidates = first_chunk[mask].head(20) if mask.any() else first_chunk.head(20)
            else:
                candidates = first_chunk.head(20)

            if not candidates.empty:
                sample_feats = candidates[feats]
                probs = model.predict_proba(sample_feats)[:, 1]

                for idx in range(min(10, len(candidates))):
                    row = candidates.iloc[idx]
                    prob = float(probs[idx])
                    risk_lvl = "HIGH" if prob >= threshold else ("MEDIUM" if prob >= threshold * 0.5 else "LOW")
                    rec_action = (
                        "Manual Review"
                        if risk_lvl == "HIGH"
                        else ("Verification" if risk_lvl == "MEDIUM" else "Approve")
                    )

                    amt_raw = str(row.get("amount", "1000"))
                    amt_val = float(amt_raw) if amt_raw.replace(".", "", 1).isdigit() else 1000.0
                    merchant_id = str(row.get("nameDest", "M999"))
                    if len(merchant_id) > 6:
                        merchant_id = merchant_id[:6]

                    app_repository.add_transaction(
                        amount=amt_val,
                        risk_score=prob,
                        risk_level=risk_lvl,
                        recommended_action=rec_action,
                        category="transfer"
                        if str(row.get("type", "")).upper() in ("TRANSFER", "CASH_OUT")
                        else "general",
                        merchant=merchant_id,
                    )
    except Exception:
        pass

    return {
        "rows": f"{total_rows:,}",
        "columns": columns,
        "fraud_rate": f"{fraud_rate:.2f}%",
        "target": "isFraud" if has_fraud_col else "N/A",
    }


@router.post("/settings/test-model")
async def test_model_api(payload: ModelTestPayload) -> dict[str, object]:
    model_path = artifact_model_path()
    threshold_path = artifact_threshold_path()
    if not model_path.exists() or not threshold_path.exists():
        raise HTTPException(status_code=503, detail="Trained model artifacts are not available yet")

    df_payload = pd.DataFrame([payload.model_dump()])
    prediction = predict_row(model_path, threshold_path, df_payload)
    threshold = load_threshold(threshold_path)
    tx_id = app_repository.add_transaction(
        amount=payload.amount,
        risk_score=float(prediction.risk_score),
        risk_level=prediction.risk_level,
        recommended_action=prediction.recommended_action,
        category="transfer" if payload.type.upper() in ("TRANSFER", "CASH_OUT") else "general",
    )

    return {
        "transaction_id": tx_id,
        "risk_score": round(float(prediction.risk_score), 4),
        "risk_level": prediction.risk_level,
        "recommended_action": prediction.recommended_action,
        "threshold": threshold,
        "decision": "REVIEW" if prediction.risk_score >= threshold else "ALLOW",
        "reasons": reasons_for_prediction(df_payload.iloc[0]),
    }
