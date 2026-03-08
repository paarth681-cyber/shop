from __future__ import annotations

from pathlib import Path

import pytest

from config.config_loader import AppSettings
from core.customers import CustomerService
from core.database import DatabaseManager
from core.inventory import InventoryService
from core.sales import SalesService
from modules.pos_system import POSSystem


@pytest.fixture
def pos_setup(tmp_path: Path):
    db = DatabaseManager(tmp_path / "pos.db")
    db.initialize_schema()

    inventory = InventoryService(db)
    customers = CustomerService(db)
    sales = SalesService(db, customer_service=customers)

    sid = db.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", ("Acme", "x"))
    pid1 = inventory.add_product("Pen", "Stationery", 5, 10, 100, 10, sid)
    pid2 = inventory.add_product("Book", "Stationery", 20, 30, 50, 5, sid)
    cid = customers.add_customer("Bob")

    pos = POSSystem(db, sales)
    return db, pos, cid, pid1, pid2


def test_pos_full_workflow(pos_setup) -> None:
    db, pos, customer_id, pid1, pid2 = pos_setup
    settings = AppSettings(tax_enabled=True, tax_rate=0.18)

    session = pos.create_session(customer_id=customer_id)

    results = pos.search_products("pen")
    assert any(row["product_id"] == pid1 for row in results)

    pos.add_product_to_cart(session, pid1, 3)
    pos.add_product_to_cart(session, pid2, 2)
    pos.adjust_quantity(session, pid1, 4)

    totals = pos.calculate_totals(session, settings.tax_enabled, settings.tax_rate)
    assert totals["subtotal"] == pytest.approx(100.0)
    assert totals["total_amount"] == pytest.approx(118.0)

    sale = pos.finalize_sale(session, payment_method="upi", tax_enabled=True, tax_rate=0.18)
    assert sale["sale_id"] > 0

    row = db.query_one("SELECT stock_quantity FROM products WHERE product_id = ?", (pid1,))
    assert row["stock_quantity"] == 96

    sale_count = db.query_one("SELECT COUNT(*) AS c FROM sales")
    assert sale_count["c"] == 1
