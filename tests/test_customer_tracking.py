from __future__ import annotations

from pathlib import Path

import pytest

from core.customers import CustomerService
from core.database import DatabaseManager
from core.inventory import InventoryService
from core.sales import SaleLineInput, SalesService


@pytest.fixture
def setup_services(tmp_path: Path):
    db = DatabaseManager(tmp_path / "customers.db")
    db.initialize_schema()
    inventory = InventoryService(db)
    customers = CustomerService(db)
    sales = SalesService(db, customer_service=customers)

    supplier_id = db.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", ("Acme", "x"))
    product_id = inventory.add_product("Notebook", "Stationery", 40, 100, 100, 10, supplier_id)
    c1 = customers.add_customer("Alice", phone="111")
    c2 = customers.add_customer("Bob", phone="222")

    return customers, sales, product_id, c1, c2


def test_revenue_and_frequency_reports(setup_services) -> None:
    customers, sales, product_id, c1, c2 = setup_services

    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=3)], c1, "cash", 0.0)
    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=2)], c1, "card", 0.0)
    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=1)], c2, "upi", 0.0)

    top = customers.most_frequent_customers(limit=2)
    assert top[0]["customer_id"] == c1
    assert int(top[0]["purchase_count"]) == 2

    revenue_rows = customers.revenue_by_customer()
    revenue_map = {int(row["customer_id"]): float(row["revenue"]) for row in revenue_rows}
    assert revenue_map[c1] == pytest.approx(500.0)
    assert revenue_map[c2] == pytest.approx(100.0)


def test_customer_purchase_summary(setup_services) -> None:
    customers, sales, product_id, c1, _ = setup_services
    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=5)], c1, "wallet", 0.1)
    summary = customers.customer_purchase_summary(c1)

    assert summary["customer_id"] == c1
    assert summary["purchase_count"] == 1
    assert summary["total_spent"] == pytest.approx(550.0)
    assert summary["average_ticket"] == pytest.approx(550.0)
