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


class TrendPoint(BaseModel):
    label: str
    volume: int
    fraud: int


class PaymentBreakdownItem(BaseModel):
    type: str
    volume: str
    share: str
    fraud_rate: str
    risk_level: str
    percent: float


class RiskDistributionItem(BaseModel):
    label: str
    count: int
    percent: float


class DashboardSummary(BaseModel):
    page_title: str = "Dashboard"
    stats: list[DashboardStat]
    recent_transactions: list[TransactionCard]
    hourly_trend: list[TrendPoint]
    payment_breakdown: list[PaymentBreakdownItem]
    risk_distribution: list[RiskDistributionItem]
