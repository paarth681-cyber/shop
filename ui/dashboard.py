"""Dashboard integration facade for modular services."""

from __future__ import annotations

from modules.reports import ReportsService
from modules.restocking import RestockingService


class DashboardService:
    """Backend facade consumable by desktop or web dashboard UI."""

    def __init__(self, reports: ReportsService, restocking: RestockingService) -> None:
        self.reports = reports
        self.restocking = restocking

    def snapshot(self) -> dict:
        return {
            "sales": self.reports.sales_summary(),
            "inventory": self.reports.inventory_summary(),
            "low_stock": [dict(row) for row in self.restocking.low_stock_alerts()],
        }
