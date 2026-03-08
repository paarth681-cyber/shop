from __future__ import annotations

from pathlib import Path

import pytest

from core.database import DatabaseManager
from core.inventory import InventoryService


@pytest.fixture
def inventory(tmp_path: Path) -> InventoryService:
    db = DatabaseManager(tmp_path / "inventory.db")
    db.initialize_schema()
    db.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", ("Acme", "acme@example.com"))
    return InventoryService(db)


def test_product_creation(inventory: InventoryService) -> None:
    product_id = inventory.add_product(
        name="USB Cable",
        category="Accessories",
        cost_price=50,
        selling_price=120,
        stock_quantity=10,
        reorder_level=3,
        supplier_id=1,
    )
    assert product_id > 0


def test_inventory_updates_and_low_stock(inventory: InventoryService) -> None:
    pid = inventory.add_product("Mouse", "Accessories", 400, 700, 5, 4, 1)
    inventory.update_stock(pid, -2)

    low = inventory.check_low_stock()
    assert any(row["product_id"] == pid for row in low)


def test_restock_order_workflow(inventory: InventoryService) -> None:
    pid = inventory.add_product("Keyboard", "Accessories", 700, 1200, 1, 5, 1)
    restock_id = inventory.create_restock_order(pid, quantity=10, supplier_id=1)
    assert restock_id > 0

    inventory.receive_restock_order(restock_id)
    low = inventory.check_low_stock()
    assert all(row["product_id"] != pid for row in low)
