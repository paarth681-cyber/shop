"""Inventory service for stock tracking and restocking workflows."""

from __future__ import annotations

import sqlite3
from typing import Optional

from core.database import DatabaseManager


class InventoryService:
    """Inventory operations with validation and restocking support."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def add_product(
        self,
        name: str,
        category: str,
        cost_price: float,
        selling_price: float,
        stock_quantity: int,
        reorder_level: int,
        supplier_id: Optional[int] = None,
    ) -> int:
        if stock_quantity < 0:
            raise ValueError("Initial stock cannot be negative")
        if reorder_level < 0:
            raise ValueError("Reorder level cannot be negative")
        if cost_price < 0 or selling_price < 0:
            raise ValueError("Prices must be non-negative")
        return self.db.execute(
            """
            INSERT INTO products (
                name, category, cost_price, selling_price,
                stock_quantity, reorder_level, supplier_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, cost_price, selling_price, stock_quantity, reorder_level, supplier_id),
        )

    def update_stock(self, product_id: int, quantity_delta: int) -> None:
        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT stock_quantity FROM products WHERE product_id = ?", (product_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"Product {product_id} not found")
            new_qty = int(row["stock_quantity"]) + int(quantity_delta)
            if new_qty < 0:
                raise ValueError("Insufficient stock")
            conn.execute(
                "UPDATE products SET stock_quantity = ? WHERE product_id = ?",
                (new_qty, product_id),
            )

    def check_low_stock(self) -> list[sqlite3.Row]:
        return self.db.query_all(
            """
            SELECT p.product_id, p.name, p.stock_quantity, p.reorder_level, s.name AS supplier_name
            FROM products p
            LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id
            WHERE p.stock_quantity < p.reorder_level
            ORDER BY p.stock_quantity ASC
            """
        )

    def create_restock_order(
        self,
        product_id: int,
        quantity: int,
        supplier_id: int,
        status: str = "pending",
    ) -> int:
        if quantity <= 0:
            raise ValueError("Restock quantity must be positive")
        valid_status = {"pending", "ordered", "received", "cancelled"}
        if status not in valid_status:
            raise ValueError(f"Invalid restock status: {status}")
        return self.db.execute(
            """
            INSERT INTO restock_orders (product_id, quantity, supplier_id, status)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, quantity, supplier_id, status),
        )

    def create_restock_orders_for_low_stock(self, multiplier: int = 2) -> list[int]:
        """Create pending restock orders for low-stock products missing active orders."""
        if multiplier <= 0:
            raise ValueError("Multiplier must be positive")
        created: list[int] = []
        with self.db.transaction() as conn:
            rows = conn.execute(
                """
                SELECT p.product_id, p.stock_quantity, p.reorder_level, p.supplier_id
                FROM products p
                WHERE p.stock_quantity < p.reorder_level
                  AND p.supplier_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM restock_orders r
                      WHERE r.product_id = p.product_id
                        AND r.status IN ('pending', 'ordered')
                  )
                """
            ).fetchall()

            for row in rows:
                deficit = int(row["reorder_level"]) - int(row["stock_quantity"])
                restock_qty = max(deficit * multiplier, 1)
                cur = conn.execute(
                    """
                    INSERT INTO restock_orders (product_id, quantity, supplier_id, status)
                    VALUES (?, ?, ?, 'pending')
                    """,
                    (row["product_id"], restock_qty, row["supplier_id"]),
                )
                created.append(int(cur.lastrowid))
        return created

    def receive_restock_order(self, restock_id: int) -> None:
        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT product_id, quantity, status FROM restock_orders WHERE restock_id = ?",
                (restock_id,),
            ).fetchone()
            if not row:
                raise ValueError(f"Restock order {restock_id} not found")
            if row["status"] == "received":
                return
            if row["status"] == "cancelled":
                raise ValueError("Cancelled restock orders cannot be received")
            conn.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                (row["quantity"], row["product_id"]),
            )
            conn.execute(
                "UPDATE restock_orders SET status = 'received' WHERE restock_id = ?",
                (restock_id,),
            )
