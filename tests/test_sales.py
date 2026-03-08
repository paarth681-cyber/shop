from __future__ import annotations

from pathlib import Path

import pytest

from core.customers import CustomerService
from core.database import DatabaseManager
from core.inventory import InventoryService
from core.sales import SaleLineInput, SalesService


@pytest.fixture
def services(tmp_path: Path):
    db = DatabaseManager(tmp_path / "sales.db")
    db.initialize_schema()

    inventory = InventoryService(db)
    customers = CustomerService(db)
    sales = SalesService(db, customer_service=customers)

    supplier_id = db.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", ("Acme", "x"))
    product_id = inventory.add_product("Laptop", "Electronics", 50000, 70000, 10, 2, supplier_id)
    customer_id = customers.add_customer("Alice", "999", "a@x.com", "Addr")

    return db, inventory, customers, sales, product_id, customer_id


def test_sale_transaction_and_stock_deduction(services) -> None:
    db, _, _, sales, product_id, customer_id = services

    result = sales.finalize_sale(
        items=[SaleLineInput(product_id=product_id, quantity=2)],
        customer_id=customer_id,
        payment_method="card",
        tax_rate=0.18,
    )

    assert result["sale_id"] > 0
    assert result["total_amount"] == pytest.approx(165200.0)

    row = db.query_one("SELECT stock_quantity FROM products WHERE product_id = ?", (product_id,))
    assert row is not None
    assert int(row["stock_quantity"]) == 8


def test_customer_sales_tracking(services) -> None:
    _, _, customers, sales, product_id, customer_id = services

    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=1)], customer_id, "cash", 0.0)
    sales.finalize_sale([SaleLineInput(product_id=product_id, quantity=1)], customer_id, "cash", 0.0)

    history = customers.get_purchase_history(customer_id)
    assert len(history) >= 2

    total = customers.total_purchases(customer_id)
    assert total == pytest.approx(140000.0)

    top = customers.most_frequent_customers(limit=1)
    assert top[0]["customer_id"] == customer_id
