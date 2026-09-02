from abc import ABC, abstractmethod
from typing import Callable

from models.dashboard import DashboardSummary


class DashboardRepository(ABC):
    @abstractmethod
    def get_summary(self) -> DashboardSummary:
        raise NotImplementedError


class DynamicDashboardRepository(DashboardRepository):
    def __init__(self, provider: Callable[[], DashboardSummary]) -> None:
        self._provider = provider

    def get_summary(self) -> DashboardSummary:
        return self._provider()

