"""Sales service with transactional POS-safe sale finalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from core.customers import CustomerService
from database.database import DatabaseManager

TWOPLACES = Decimal("0.01")
VALID_PAYMENT_METHODS = {"cash", "card", "upi", "wallet", "bank_transfer", "other"}


def _money(value: Decimal) -> float:
    return float(value.quantize(TWOPLACES, rounding=ROUND_HALF_UP))


@dataclass(slots=True)
class SaleLineInput:
    product_id: int
    quantity: int


class SalesService:
    """Sale transaction orchestration and receipt data retrieval."""

    def __init__(self, db: DatabaseManager, customer_service: Optional[CustomerService] = None) -> None:
        self.db = db
        self.customer_service = customer_service or CustomerService(db)

    def finalize_sale(
        self,
        items: list[SaleLineInput],
        customer_id: Optional[int],
        payment_method: str,
        tax_rate: float = 0.0,
    ) -> dict:
        if not items:
            raise ValueError("Cannot finalize sale with empty cart")
        if payment_method not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method: {payment_method}")
        if tax_rate < 0:
            raise ValueError("Tax rate cannot be negative")

        with self.db.transaction() as conn:
            subtotal = Decimal("0.00")
            line_records: list[tuple[int, str, int, Decimal]] = []

            for item in items:
                if item.quantity <= 0:
                    raise ValueError("Quantity must be positive")

                product = conn.execute(
                    """
                    SELECT product_id, name, selling_price, stock_quantity
                    FROM products
                    WHERE product_id = ?
                    """,
                    (item.product_id,),
                ).fetchone()
                if not product:
                    raise ValueError(f"Product {item.product_id} does not exist")
                if int(product["stock_quantity"]) < item.quantity:
                    raise ValueError(f"Insufficient stock for {product['name']}")

                unit_price = Decimal(str(product["selling_price"]))
                line_total = unit_price * Decimal(item.quantity)
                subtotal += line_total
                line_records.append((item.product_id, product["name"], item.quantity, unit_price))

            tax_amount = subtotal * Decimal(str(tax_rate))
            total_amount = subtotal + tax_amount

            sale_cur = conn.execute(
                """
                INSERT INTO sales (datetime, customer_id, total_amount, payment_method)
                VALUES (?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(timespec="seconds"),
                    customer_id,
                    _money(total_amount),
                    payment_method,
                ),
            )
            sale_id = int(sale_cur.lastrowid)

            for product_id, _, quantity, unit_price in line_records:
                conn.execute(
                    """
                    INSERT INTO sale_items (sale_id, product_id, quantity, price_at_sale)
                    VALUES (?, ?, ?, ?)
                    """,
                    (sale_id, product_id, quantity, _money(unit_price)),
                )
                conn.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                    (quantity, product_id),
                )

        if customer_id is not None:
            self.customer_service.add_loyalty_points_for_sale(customer_id, float(total_amount))

        return {
            "sale_id": sale_id,
            "subtotal": _money(subtotal),
            "tax_amount": _money(tax_amount),
            "total_amount": _money(total_amount),
            "payment_method": payment_method,
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": p,
                    "product_name": name,
                    "quantity": q,
                    "price_at_sale": _money(price),
                    "line_total": _money(price * Decimal(q)),
                }
                for (p, name, q, price) in line_records
            ],
        }

    def get_sale_receipt(self, sale_id: int) -> dict:
        sale = self.db.query_one(
            """
            SELECT s.sale_id, s.datetime, s.customer_id, c.name AS customer_name,
                   s.total_amount, s.payment_method
            FROM sales s
            LEFT JOIN customers c ON c.customer_id = s.customer_id
            WHERE s.sale_id = ?
            """,
            (sale_id,),
        )
        if not sale:
            raise ValueError(f"Sale {sale_id} not found")

        items = self.db.query_all(
            """
            SELECT si.product_id, p.name AS product_name, si.quantity, si.price_at_sale,
                   (si.quantity * si.price_at_sale) AS line_total
            FROM sale_items si
            JOIN products p ON p.product_id = si.product_id
            WHERE si.sale_id = ?
            ORDER BY si.sale_item_id
            """,
            (sale_id,),
        )
        subtotal = sum(Decimal(str(row["line_total"])) for row in items) if items else Decimal("0.00")

        return {
            "sale_id": sale["sale_id"],
            "datetime": sale["datetime"],
            "customer_id": sale["customer_id"],
            "customer_name": sale["customer_name"],
            "subtotal": _money(subtotal),
            "total_amount": float(sale["total_amount"]),
            "payment_method": sale["payment_method"],
            "items": [dict(row) for row in items],
        }
