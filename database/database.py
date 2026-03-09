"""Database manager and schema initialization for Shop Manager Pro."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterable, Optional


def _load_default_schema() -> str:
    schema_path = Path(__file__).with_name("schema.sql")
    return schema_path.read_text(encoding="utf-8")


DEFAULT_SCHEMA = _load_default_schema()


class DatabaseManager:
    """Lightweight database manager with explicit transaction control."""

    def __init__(self, db_path: str | Path = "shop_manager_modular.db") -> None:
        self.db_path = Path(db_path)

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self._create_connection()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def initialize_schema(self, schema_sql: str = DEFAULT_SCHEMA) -> None:
        with self.connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
        with self.connection() as conn:
            cur = conn.execute(sql, tuple(params))
            conn.commit()
            return int(cur.lastrowid)

    def query_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        with self.connection() as conn:
            cur = conn.execute(sql, tuple(params))
            return cur.fetchone()

    def query_all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self.connection() as conn:
            cur = conn.execute(sql, tuple(params))
            return list(cur.fetchall())
