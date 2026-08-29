from pydantic import BaseModel


class DashboardStat(BaseModel):
    label: str
    value: str


class TransactionCard(BaseModel):
    id: str
    amount: str
    risk_level: str
    risk_score: str
    action: str


class DashboardSummary(BaseModel):
    page_title: str = "Dashboard"
    stats: list[DashboardStat]
    recent_transactions: list[TransactionCard]
