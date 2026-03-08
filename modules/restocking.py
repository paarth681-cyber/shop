"""Restocking module built on inventory service."""

from __future__ import annotations

from core.inventory import InventoryService


class RestockingService:
    """Business-friendly restock workflow wrappers."""

    def __init__(self, inventory: InventoryService) -> None:
        self.inventory = inventory

    def low_stock_alerts(self):
        return self.inventory.check_low_stock()

    def create_restock_order(self, product_id: int, quantity: int, supplier_id: int) -> int:
        return self.inventory.create_restock_order(
            product_id=product_id,
            quantity=quantity,
            supplier_id=supplier_id,
            status="ordered",
        )

    def auto_create_restock_orders(self, multiplier: int = 2) -> list[int]:
        return self.inventory.create_restock_orders_for_low_stock(multiplier=multiplier)

    def mark_received(self, restock_id: int) -> None:
        self.inventory.receive_restock_order(restock_id)
