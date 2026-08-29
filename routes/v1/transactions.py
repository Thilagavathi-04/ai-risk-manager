from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.repositories import app_repository
from paths import TEMPLATES_DIR


router = APIRouter(prefix="/transactions", tags=["transactions-v1"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("")
async def list_transactions(request: Request) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Transaction Queue",
        "transactions": app_repository.list_transactions(),
    }
    return templates.TemplateResponse(request=request, name="pages/transactions.html", context=context)


@router.get("/{transaction_id}", response_class=HTMLResponse)
async def transaction_detail(request: Request, transaction_id: str) -> HTMLResponse:
    context = {
        "request": request,
        "page_title": "Transaction Detail",
        "transaction": app_repository.get_transaction(transaction_id),
    }
    return templates.TemplateResponse(request=request, name="pages/transaction_detail.html", context=context)
