"""Customer service functions for analytics and tracking."""

from __future__ import annotations

import sqlite3
from typing import Optional

from database.database import DatabaseManager


class CustomerService:
    """Service for customer CRUD and customer-level sales analytics."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def add_customer(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        loyalty_points: int = 0,
    ) -> int:
        if loyalty_points < 0:
            raise ValueError("Loyalty points cannot be negative")
        return self.db.execute(
            """
            INSERT INTO customers (name, phone, email, address, loyalty_points)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, phone, email, address, loyalty_points),
        )

    def get_purchase_history(self, customer_id: int) -> list[sqlite3.Row]:
        return self.db.query_all(
            """
            SELECT s.sale_id, s.datetime, s.total_amount, s.payment_method,
                   si.product_id, p.name AS product_name, si.quantity, si.price_at_sale
            FROM sales s
            JOIN sale_items si ON si.sale_id = s.sale_id
            JOIN products p ON p.product_id = si.product_id
            WHERE s.customer_id = ?
            ORDER BY s.datetime DESC, s.sale_id DESC
            """,
            (customer_id,),
        )

    def total_purchases(self, customer_id: int) -> float:
        row = self.db.query_one(
            "SELECT COALESCE(SUM(total_amount), 0) AS total FROM sales WHERE customer_id = ?",
            (customer_id,),
        )
        return float(row["total"]) if row else 0.0

    def most_frequent_customers(self, limit: int = 10) -> list[sqlite3.Row]:
        if limit <= 0:
            raise ValueError("Limit must be positive")
        return self.db.query_all(
            """
            SELECT c.customer_id, c.name, COUNT(s.sale_id) AS purchase_count,
                   COALESCE(SUM(s.total_amount), 0) AS revenue
            FROM customers c
            LEFT JOIN sales s ON s.customer_id = c.customer_id
            GROUP BY c.customer_id, c.name
            ORDER BY purchase_count DESC, revenue DESC
            LIMIT ?
            """,
            (limit,),
        )

    def revenue_by_customer(self) -> list[sqlite3.Row]:
        return self.db.query_all(
            """
            SELECT c.customer_id, c.name, COALESCE(SUM(s.total_amount), 0) AS revenue
            FROM customers c
            LEFT JOIN sales s ON s.customer_id = c.customer_id
            GROUP BY c.customer_id, c.name
            ORDER BY revenue DESC
            """
        )

    def customer_purchase_summary(self, customer_id: int) -> dict:
        row = self.db.query_one(
            """
            SELECT
                c.customer_id,
                c.name,
                c.loyalty_points,
                COUNT(s.sale_id) AS purchase_count,
                COALESCE(SUM(s.total_amount), 0) AS total_spent,
                COALESCE(AVG(s.total_amount), 0) AS average_ticket
            FROM customers c
            LEFT JOIN sales s ON s.customer_id = c.customer_id
            WHERE c.customer_id = ?
            GROUP BY c.customer_id, c.name, c.loyalty_points
            """,
            (customer_id,),
        )
        if not row:
            raise ValueError(f"Customer {customer_id} not found")
        return {
            "customer_id": int(row["customer_id"]),
            "name": row["name"],
            "loyalty_points": int(row["loyalty_points"]),
            "purchase_count": int(row["purchase_count"]),
            "total_spent": float(row["total_spent"]),
            "average_ticket": float(row["average_ticket"]),
        }

    def add_loyalty_points_for_sale(self, customer_id: int, total_amount: float) -> None:
        points = int(total_amount // 100)
        if points <= 0:
            return
        self.db.execute(
            "UPDATE customers SET loyalty_points = loyalty_points + ? WHERE customer_id = ?",
            (points, customer_id),
        )
