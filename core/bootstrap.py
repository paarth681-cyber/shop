"""Bootstrap utilities to wire modular services based on configuration."""

from __future__ import annotations

from dataclasses import dataclass

from config.config_loader import AppSettings, load_enabled_modules, load_settings
from core.customers import CustomerService
from database.database import DatabaseManager
from core.inventory import InventoryService
from core.sales import SalesService
from modules.pos_system import POSSystem
from modules.reports import ReportsService
from modules.restocking import RestockingService


@dataclass(slots=True)
class AppContext:
    settings: AppSettings
    db: DatabaseManager
    customers: CustomerService
    inventory: InventoryService
    sales: SalesService
    pos: POSSystem
    reports: ReportsService
    restocking: RestockingService
    enabled_modules: dict


def build_app_context(db_path: str = "shop_manager_modular.db") -> AppContext:
    settings = load_settings()
    db = DatabaseManager(db_path)
    db.initialize_schema()

    customers = CustomerService(db)
    inventory = InventoryService(db)
    sales = SalesService(db, customer_service=customers)
    pos = POSSystem(db, sales)
    reports = ReportsService(db, customers)
    restocking = RestockingService(inventory)
    enabled_modules = load_enabled_modules(settings)

    return AppContext(
        settings=settings,
        db=db,
        customers=customers,
        inventory=inventory,
        sales=sales,
        pos=pos,
        reports=reports,
        restocking=restocking,
        enabled_modules=enabled_modules,
    )
