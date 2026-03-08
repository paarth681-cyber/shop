"""POS interface adapter for GUI/web layers."""

from __future__ import annotations

from modules.pos_system import POSSession, POSSystem


class POSInterface:
    """Thin adapter that UI layers can call directly."""

    def __init__(self, pos_system: POSSystem) -> None:
        self.pos_system = pos_system

    def start_sale(self, customer_id: int | None = None) -> POSSession:
        return self.pos_system.create_session(customer_id)

    def search_products(self, query: str):
        return self.pos_system.search_products(query)

    def add_item(self, session: POSSession, product_id: int, qty: int = 1) -> None:
        self.pos_system.add_product_to_cart(session, product_id, qty)

    def set_quantity(self, session: POSSession, product_id: int, qty: int) -> None:
        self.pos_system.adjust_quantity(session, product_id, qty)

    def totals(self, session: POSSession, tax_enabled: bool, tax_rate: float) -> dict:
        return self.pos_system.calculate_totals(session, tax_enabled, tax_rate)

    def checkout(self, session: POSSession, payment_method: str, tax_enabled: bool, tax_rate: float) -> dict:
        return self.pos_system.finalize_sale(session, payment_method, tax_enabled, tax_rate)
