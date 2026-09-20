# Stage 2 Audit & Reconciliation

Retail360 stores load evidence in the `audit` schema.

## Tables

- `audit.load_run` — one record per ingestion execution
- `audit.table_load` — loaded row count by table and source file
- `audit.row_reconciliation` — expected-vs-actual source row checks

## Why this exists

A portfolio-grade warehouse should not only load data; it should prove that the load was complete and reproducible.

The Stage 2 gate requires exact reconciliation for all 14 scoped source tables.
