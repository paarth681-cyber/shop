from __future__ import annotations

from pathlib import Path

import pytest

from core.database import DatabaseManager


@pytest.fixture
def db(tmp_path: Path) -> DatabaseManager:
    db_path = tmp_path / "test_shop.db"
    manager = DatabaseManager(db_path)
    manager.initialize_schema()
    return manager


def test_database_creation(db: DatabaseManager) -> None:
    tables = {
        row["name"]
        for row in db.query_all("SELECT name FROM sqlite_master WHERE type='table'")
    }
    expected = {
        "products",
        "customers",
        "sales",
        "sale_items",
        "suppliers",
        "restock_orders",
    }
    assert expected.issubset(tables)


def test_foreign_keys_enabled(db: DatabaseManager) -> None:
    with db.connection() as conn:
        row = conn.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1
