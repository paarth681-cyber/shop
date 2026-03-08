# Shop Manager Pro - Architecture Analysis (March 6, 2026)

## Overall architecture
- The codebase has two parallel implementations:
`shop_manager_pro_qt.py` (legacy UI-centric monolith) and a newer modular backend (`core/`, `modules/`, `ui/`, `config/`).
- The modular backend is usable headlessly and already aligns with service-based architecture for POS, inventory, and reporting.

## Current database behavior
- Legacy UI code uses direct SQLite access (`shop.db` / `shop_manager.db`) with repeated SQL in UI handlers.
- Modular backend uses `DatabaseManager` with centralized schema and service methods.
- Before this refactor, schema definitions were duplicated between `core/database.py` and `core/schema.sql`.

## Current POS implementation
- Legacy POS exists inside Qt widget logic with DB writes in UI handlers.
- Modular POS (`modules/pos_system.py` + `core/sales.py`) supports:
  product search, cart mutations, totals, customer linkage, sale finalization, stock deduction, and receipt retrieval.

## Current inventory handling
- Inventory is handled via `core/inventory.py`:
  add/update product stock, low-stock checks, restock order create/receive.
- Before this refactor, restock automation and stronger order-state validation were limited.

## Weaknesses identified
- Architectural split between monolith and modular backend increases maintenance overhead.
- Legacy auth in Qt flow validates plaintext passwords.
- Float-based money math in parts of modular sales flow risked precision drift.
- Module loading lacked whitelist/guardrails.

## Security concerns
- Plaintext credential checks exist in legacy UI (`shop_manager_pro_qt.py`).
- Default credentials are documented in project docs.

## Performance concerns
- Legacy code opens many short-lived DB connections and runs repeated ad-hoc queries.
- Missing composite indexes for some reporting/access patterns.

## Improvement plan executed
1. Consolidate schema source of truth in `core/schema.sql` and load it from `core/database.py`.
2. Harden DB layer with transactional context, foreign key enforcement, WAL mode, and busy timeout.
3. Strengthen POS/sales/inventory logic for transactional integrity and validation.
4. Extend customer analytics and restock automation flows.
5. Add dedicated pytest modules for customer tracking and restocking workflows.
6. Keep legacy UI untouched to avoid functional regressions while improving modular backend.
