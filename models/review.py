from pydantic import BaseModel


class ReviewItem(BaseModel):
    transaction_id: str
    score: str
    amount: str
    recommendation: str
    status: str


class ReviewAction(BaseModel):
    transaction_id: str
    reviewer_outcome: str
