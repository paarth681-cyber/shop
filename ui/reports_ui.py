"""Reports interface adapter."""

from __future__ import annotations

from modules.reports import ReportsService


class ReportsInterface:
    """UI-friendly wrapper around report queries."""

    def __init__(self, reports: ReportsService) -> None:
        self.reports = reports

    def load_sales(self) -> dict:
        return self.reports.sales_summary()

    def load_inventory(self) -> dict:
        return self.reports.inventory_summary()

    def load_customer_revenue(self):
        return [dict(row) for row in self.reports.customer_revenue_report()]
