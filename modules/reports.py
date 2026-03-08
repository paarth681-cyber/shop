"""Reporting functions for sales, inventory, and customers."""

from __future__ import annotations

from core.customers import CustomerService
from core.database import DatabaseManager


class ReportsService:
    """Aggregated reporting queries used by dashboard and reports UI."""

    def __init__(self, db: DatabaseManager, customers: CustomerService) -> None:
        self.db = db
        self.customers = customers

    def sales_summary(self) -> dict:
        row = self.db.query_one(
            """
            SELECT COUNT(*) AS sales_count, COALESCE(SUM(total_amount), 0) AS revenue,
                   COALESCE(AVG(total_amount), 0) AS avg_sale
            FROM sales
            """
        )
        return {
            "sales_count": int(row["sales_count"]),
            "revenue": float(row["revenue"]),
            "avg_sale": float(row["avg_sale"]),
        }

    def inventory_summary(self) -> dict:
        row = self.db.query_one(
            """
            SELECT COUNT(*) AS products,
                   COALESCE(SUM(stock_quantity), 0) AS total_units,
                   COALESCE(SUM(stock_quantity * cost_price), 0) AS inventory_cost_value
            FROM products
            """
        )
        return {
            "products": int(row["products"]),
            "total_units": int(row["total_units"]),
            "inventory_cost_value": float(row["inventory_cost_value"]),
        }

    def customer_revenue_report(self):
        return self.customers.revenue_by_customer()
