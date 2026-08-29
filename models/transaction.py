from pydantic import BaseModel


class TransactionListItem(BaseModel):
    id: str
    timestamp: str
    amount: str
    merchant: str
    category: str
    risk_score: str
    risk_level: str
    recommended_action: str
    review_status: str


class TransactionDetail(BaseModel):
    id: str
    timestamp: str
    amount: str
    merchant: str
    category: str
    risk_score: str
    risk_level: str
    recommended_action: str
    review_status: str
    signals: list[str]
    historical_context: list[tuple[str, str]]
