from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/settings", tags=["settings-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def settings(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Settings",
        "sections": app_repository.settings(),
    }
    return templates.TemplateResponse(request=request, name="pages/settings.html", context=context)
