from pydantic import BaseModel


class AuditEntry(BaseModel):
    timestamp: str
    transaction_id: str
    model_version: str
    score: str
    threshold: str
    decision: str
    reviewer_outcome: str
