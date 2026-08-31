from abc import ABC, abstractmethod
from typing import Callable

from models.dashboard import DashboardSummary, DashboardStat, TransactionCard


class DashboardRepository(ABC):
    @abstractmethod
    def get_summary(self) -> DashboardSummary:
        raise NotImplementedError


class DynamicDashboardRepository(DashboardRepository):
    def __init__(self, provider: Callable[[], DashboardSummary]) -> None:
        self._provider = provider

    def get_summary(self) -> DashboardSummary:
        return self._provider()


class InMemoryDashboardRepository(DashboardRepository):
    def get_summary(self) -> DashboardSummary:
        return DashboardSummary(
            stats=[
                DashboardStat(label="Transactions", value="12,482"),
                DashboardStat(label="High Risk", value="183"),
                DashboardStat(label="Review Queue", value="64"),
                DashboardStat(label="Precision", value="91.2%"),
                DashboardStat(label="Recall", value="78.6%"),
            ],
            recent_transactions=[
                TransactionCard(
                    id="TX1001",
                    amount="₹8,200",
                    risk_level="HIGH",
                    risk_score="87%",
                    action="Manual Review",
                ),
                TransactionCard(
                    id="TX1002",
                    amount="₹1,200",
                    risk_level="LOW",
                    risk_score="21%",
                    action="Approve",
                ),
            ],
        )

