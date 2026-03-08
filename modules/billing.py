"""Billing helpers for totals and receipt formatting."""

from __future__ import annotations

from typing import Any


def calculate_totals(subtotal: float, tax_enabled: bool, tax_rate: float) -> dict[str, float]:
    tax_amount = subtotal * tax_rate if tax_enabled else 0.0
    return {
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total_amount": round(subtotal + tax_amount, 2),
    }


def format_receipt(receipt_data: dict[str, Any], currency: str = "INR") -> str:
    lines = [
        "SHOP MANAGER PRO",
        f"Sale ID: {receipt_data['sale_id']}",
        f"Date: {receipt_data.get('datetime', 'N/A')}",
        f"Customer: {receipt_data.get('customer_name') or 'Walk-in'}",
        "-" * 32,
    ]

    for item in receipt_data.get("items", []):
        line_total = float(item["line_total"])
        lines.append(
            f"{item['product_name']} x{item['quantity']} @ {currency} {float(item['price_at_sale']):.2f} = {currency} {line_total:.2f}"
        )

    lines.extend(
        [
            "-" * 32,
            f"TOTAL: {currency} {float(receipt_data.get('total_amount', 0.0)):.2f}",
        ]
    )
    return "\n".join(lines)
