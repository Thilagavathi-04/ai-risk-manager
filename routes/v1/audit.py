from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/audit", tags=["audit-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def audit_log(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Audit Log",
        "entries": app_repository.audit_entries(),
    }
    return templates.TemplateResponse(request=request, name="pages/audit.html", context=context)
