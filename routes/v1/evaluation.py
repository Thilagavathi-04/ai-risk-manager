from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/evaluation", tags=["evaluation-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def evaluation(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Evaluation",
        "metrics": app_repository.evaluation_metrics(),
        "threshold_cost_points": app_repository.threshold_cost_points(),
        "model_comparison": app_repository.model_comparison(),
        "confusion_matrix": app_repository.confusion_matrix(),
        "selected_threshold": "0.72",
    }
    return templates.TemplateResponse(request=request, name="pages/evaluation.html", context=context)
