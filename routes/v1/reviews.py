from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from logging_config import configure_logging
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/reviews", tags=["reviews-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
logger = configure_logging()


@router.get("")
async def list_reviews(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Review Queue",
        "reviews": app_repository.list_reviews(),
    }
    return templates.TemplateResponse(request=request, name="pages/reviews.html", context=context)


@router.post("/{transaction_id}")
async def record_review(transaction_id: str, reviewer_outcome: str = Form(...)) -> RedirectResponse:
    app_repository.record_review(transaction_id, reviewer_outcome)
    logger.info("Recorded review for %s with outcome %s", transaction_id, reviewer_outcome)
    return RedirectResponse(url=f"/transactions/{transaction_id}", status_code=303)
