from __future__ import annotations

from pathlib import Path

import pytest

from core.database import DatabaseManager
from core.inventory import InventoryService


@pytest.fixture
def inventory(tmp_path: Path) -> InventoryService:
    db = DatabaseManager(tmp_path / "restocking.db")
    db.initialize_schema()
    db.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", ("Global Supplier", "x"))
    return InventoryService(db)


def test_auto_create_restock_orders(inventory: InventoryService) -> None:
    low_product = inventory.add_product("Router", "Electronics", 1200, 1900, 2, 6, 1)
    inventory.add_product("Cable", "Accessories", 50, 120, 30, 5, 1)

    restock_ids = inventory.create_restock_orders_for_low_stock(multiplier=2)
    assert len(restock_ids) == 1

    orders = inventory.db.query_all(
        "SELECT product_id, quantity, status FROM restock_orders WHERE restock_id = ?",
        (restock_ids[0],),
    )
    assert int(orders[0]["product_id"]) == low_product
    assert int(orders[0]["quantity"]) == 8
    assert orders[0]["status"] == "pending"


def test_receive_restock_updates_stock(inventory: InventoryService) -> None:
    product_id = inventory.add_product("SSD", "Electronics", 3000, 4200, 1, 10, 1)
    restock_id = inventory.create_restock_order(product_id=product_id, quantity=15, supplier_id=1, status="ordered")
    inventory.receive_restock_order(restock_id)

    product = inventory.db.query_one("SELECT stock_quantity FROM products WHERE product_id = ?", (product_id,))
    order = inventory.db.query_one("SELECT status FROM restock_orders WHERE restock_id = ?", (restock_id,))

    assert int(product["stock_quantity"]) == 16
    assert order["status"] == "received"


def test_receive_cancelled_restock_raises(inventory: InventoryService) -> None:
    product_id = inventory.add_product("Printer", "Electronics", 4500, 6000, 0, 2, 1)
    restock_id = inventory.create_restock_order(product_id=product_id, quantity=4, supplier_id=1, status="cancelled")
    with pytest.raises(ValueError):
        inventory.receive_restock_order(restock_id)
