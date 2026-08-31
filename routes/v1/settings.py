import io

import pandas as pd
from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from ml_pipeline.artifacts import artifact_model_path, artifact_threshold_path, load_active_model_context, load_model_bundle
from ml_pipeline.features import feature_columns
from ml_pipeline.data_validation import validate_dataset
from ml_pipeline.predict import predict_row, reasons_for_prediction
from ml_pipeline.threshold import load_threshold
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/settings", tags=["settings-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _base_settings_context(request: Request, test_summary: dict | None = None, model_test: dict | None = None) -> dict:
    context = {
        "request": request,
        "page_title": "Settings",
        "sections": app_repository.settings(),
        "model_context": load_active_model_context(),
        "test_summary": test_summary,
        "model_test": model_test,
    }
    return context


@router.get("")
async def settings(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="pages/settings.html", context=_base_settings_context(request))


@router.post("/test-data")
async def validate_test_data(request: Request, file: UploadFile) -> HTMLResponse:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        # Read header and first sample chunk to validate dataset schema
        first_chunk = pd.read_csv(file.file, nrows=1000)
        validate_dataset(first_chunk)

        # Stream counts in chunks to prevent high RAM memory spikes on large datasets
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

    except Exception as exc:  # pragma: no cover - surfaced to the UI
        raise HTTPException(status_code=400, detail=f"CSV validation failed: {exc}") from exc

    fraud_rate = (total_fraud / total_rows * 100) if total_rows > 0 else 0.0

    # Score sample records prioritizing high-risk/fraud candidates and send to app repository
    try:
        model_path = artifact_model_path()
        threshold_path = artifact_threshold_path()
        if model_path.exists() and threshold_path.exists():
            model = load_model_bundle(model_path)
            threshold = load_threshold(threshold_path)
            feats = feature_columns(first_chunk)

            # Prioritize candidate rows (actual fraud or transfer/cash_out types)
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

    test_summary = {
        "rows": f"{total_rows:,}",
        "columns": columns,
        "fraud_rate": f"{fraud_rate:.2f}%",
        "target": "isFraud" if has_fraud_col else "N/A",
    }
    return templates.TemplateResponse(
        request=request,
        name="pages/settings.html",
        context=_base_settings_context(request, test_summary=test_summary),
    )


@router.post("/test-model")
async def test_model_from_form(
    request: Request,
    step: int = Form(...),
    type: str = Form(...),
    amount: float = Form(...),
    oldbalanceOrg: float = Form(...),
    newbalanceOrig: float = Form(...),
    oldbalanceDest: float = Form(...),
    newbalanceDest: float = Form(...),
) -> HTMLResponse:
    model_path = artifact_model_path()
    threshold_path = artifact_threshold_path()
    if not model_path.exists() or not threshold_path.exists():
        raise HTTPException(status_code=503, detail="Trained model artifacts are not available yet")

    payload = pd.DataFrame([
        {
            "step": step,
            "type": type,
            "amount": amount,
            "oldbalanceOrg": oldbalanceOrg,
            "newbalanceOrig": newbalanceOrig,
            "oldbalanceDest": oldbalanceDest,
            "newbalanceDest": newbalanceDest,
        }
    ])
    prediction = predict_row(model_path, threshold_path, payload)
    threshold = load_threshold(threshold_path)
    tx_id = app_repository.add_transaction(
        amount=amount,
        risk_score=float(prediction.risk_score),
        risk_level=prediction.risk_level,
        recommended_action=prediction.recommended_action,
        category="transfer" if type in ("TRANSFER", "CASH_OUT") else "general",
    )
    result = {
        "transaction_id": tx_id,
        "risk_score": round(float(prediction.risk_score), 4),
        "risk_level": prediction.risk_level,
        "recommended_action": prediction.recommended_action,
        "threshold": threshold,
        "decision": "REVIEW" if prediction.risk_score >= threshold else "ALLOW",
        "reasons": reasons_for_prediction(payload.iloc[0]),
    }
    return templates.TemplateResponse(
        request=request,
        name="pages/settings.html",
        context=_base_settings_context(request, model_test=result),
    )
