"""Config loader and module bootstrap for configurable architecture."""

from __future__ import annotations

import importlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

LOGGER = logging.getLogger(__name__)
DEFAULT_ENABLED_MODULES = ["pos_system", "billing", "reports", "restocking"]
ALLOWED_MODULES = {"pos_system", "billing", "reports", "restocking"}


@dataclass(slots=True)
class AppSettings:
    enabled_modules: list[str] = field(default_factory=lambda: DEFAULT_ENABLED_MODULES.copy())
    currency: str = "INR"
    tax_enabled: bool = True
    tax_rate: float = 0.18


def load_settings(path: str | Path = Path("config") / "settings.json") -> AppSettings:
    settings_path = Path(path)
    if not settings_path.exists():
        return AppSettings()

    with settings_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    requested_modules = list(data.get("enabled_modules", DEFAULT_ENABLED_MODULES))
    enabled_modules = [m for m in requested_modules if m in ALLOWED_MODULES]
    if not enabled_modules:
        enabled_modules = DEFAULT_ENABLED_MODULES.copy()

    tax_rate = float(data.get("tax_rate", 0.18))
    if tax_rate < 0:
        tax_rate = 0.0

    return AppSettings(
        enabled_modules=enabled_modules,
        currency=str(data.get("currency", "INR")).upper(),
        tax_enabled=bool(data.get("tax_enabled", True)),
        tax_rate=tax_rate,
    )


def load_enabled_modules(settings: AppSettings, package: str = "modules") -> dict[str, ModuleType]:
    loaded: dict[str, ModuleType] = {}
    for module_name in settings.enabled_modules:
        try:
            loaded[module_name] = importlib.import_module(f"{package}.{module_name}")
        except Exception:
            LOGGER.exception("Failed to load module '%s'", module_name)
    return loaded
