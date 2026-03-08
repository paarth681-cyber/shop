"""POS workflow service for GUI/web integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.database import DatabaseManager
from core.sales import SaleLineInput, SalesService
from modules.billing import calculate_totals


@dataclass(slots=True)
class POSSession:
    customer_id: Optional[int] = None
    cart: dict[int, int] = field(default_factory=dict)


class POSSystem:
    """Headless POS service implementing cart and checkout workflow."""

    def __init__(self, db: DatabaseManager, sales_service: SalesService) -> None:
        self.db = db
        self.sales_service = sales_service

    def create_session(self, customer_id: Optional[int] = None) -> POSSession:
        return POSSession(customer_id=customer_id)

    def search_products(self, query: str, limit: int = 20):
        pattern = f"%{query.lower()}%"
        return self.db.query_all(
            """
            SELECT product_id, name, category, selling_price, stock_quantity, reorder_level
            FROM products
            WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?
            ORDER BY name
            LIMIT ?
            """,
            (pattern, pattern, limit),
        )

    def set_customer(self, session: POSSession, customer_id: Optional[int]) -> None:
        session.customer_id = customer_id

    def add_product_to_cart(self, session: POSSession, product_id: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        product = self.db.query_one(
            "SELECT stock_quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        if not product:
            raise ValueError(f"Product {product_id} does not exist")
        current = session.cart.get(product_id, 0)
        desired = current + quantity
        if desired > int(product["stock_quantity"]):
            raise ValueError(f"Cannot add quantity beyond stock ({product['stock_quantity']})")
        session.cart[product_id] = desired

    def adjust_quantity(self, session: POSSession, product_id: int, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if quantity == 0:
            session.cart.pop(product_id, None)
            return
        product = self.db.query_one(
            "SELECT stock_quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        if not product:
            raise ValueError(f"Product {product_id} does not exist")
        if quantity > int(product["stock_quantity"]):
            raise ValueError(f"Cannot set quantity beyond stock ({product['stock_quantity']})")
        session.cart[product_id] = quantity

    def clear_cart(self, session: POSSession) -> None:
        session.cart.clear()

    def calculate_totals(self, session: POSSession, tax_enabled: bool, tax_rate: float) -> dict:
        subtotal = 0.0
        line_items: list[dict] = []

        for product_id, quantity in session.cart.items():
            row = self.db.query_one(
                "SELECT name, selling_price FROM products WHERE product_id = ?",
                (product_id,),
            )
            if not row:
                continue
            price = float(row["selling_price"])
            line_total = price * quantity
            subtotal += line_total
            line_items.append(
                {
                    "product_id": product_id,
                    "product_name": row["name"],
                    "quantity": quantity,
                    "unit_price": round(price, 2),
                    "line_total": round(line_total, 2),
                }
            )

        totals = calculate_totals(subtotal, tax_enabled=tax_enabled, tax_rate=tax_rate)
        totals["line_items"] = line_items
        return totals

    def finalize_sale(
        self,
        session: POSSession,
        payment_method: str,
        tax_enabled: bool,
        tax_rate: float,
    ) -> dict:
        if not session.cart:
            raise ValueError("Cannot finalize sale with an empty cart")
        items = [SaleLineInput(product_id=pid, quantity=qty) for pid, qty in session.cart.items()]
        sale_result = self.sales_service.finalize_sale(
            items=items,
            customer_id=session.customer_id,
            payment_method=payment_method,
            tax_rate=(tax_rate if tax_enabled else 0.0),
        )
        session.cart.clear()
        return sale_result
