"""Core domain models for Shop Manager Pro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class Supplier:
    supplier_id: int
    name: str
    contact_info: Optional[str] = None


@dataclass(slots=True)
class Product:
    product_id: int
    name: str
    category: str
    cost_price: Decimal
    selling_price: Decimal
    stock_quantity: int
    reorder_level: int
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None


@dataclass(slots=True)
class Customer:
    customer_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    loyalty_points: int = 0


@dataclass(slots=True)
class Sale:
    sale_id: int
    created_at: datetime
    customer_id: Optional[int]
    total_amount: Decimal
    payment_method: str


@dataclass(slots=True)
class SaleItem:
    sale_item_id: int
    sale_id: int
    product_id: int
    quantity: int
    price_at_sale: Decimal


@dataclass(slots=True)
class RestockOrder:
    restock_id: int
    product_id: int
    quantity: int
    supplier_id: int
    date_ordered: datetime
    status: str
