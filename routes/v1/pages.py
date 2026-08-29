from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from paths import TEMPLATES_DIR


router = APIRouter(tags=["pages-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    summary = app_repository.dashboard.get_summary()
    context = {
        "request": request,
        "page_title": summary.page_title,
        "stats": summary.stats,
        "recent_transactions": summary.recent_transactions,
    }
    return templates.TemplateResponse(request=request, name="pages/dashboard.html", context=context)

