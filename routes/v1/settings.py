import io

import pandas as pd
from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from ml_pipeline.artifacts import artifact_model_path, artifact_threshold_path, load_active_model_context
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
        contents = await file.read()
        frame = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        validate_dataset(frame)
    except Exception as exc:  # pragma: no cover - surfaced to the UI
        raise HTTPException(status_code=400, detail=f"CSV validation failed: {exc}") from exc

    fraud_rate = float(frame["isFraud"].mean() * 100)
    test_summary = {
        "rows": len(frame),
        "columns": list(frame.columns),
        "fraud_rate": f"{fraud_rate:.1f}%",
        "target": "isFraud",
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
    result = {
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
