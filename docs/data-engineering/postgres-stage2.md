# Stage 2 — PostgreSQL Warehouse Foundation

## Objective

Build a reproducible PostgreSQL warehouse foundation for Retail360 after the source layer has passed validation.

## Layering

- `raw`: source-aligned landing tables; all source attributes are stored as text with lineage metadata.
- `staging`: typed, cleaned and standardised transformations.
- `analytics`: business-ready dimensional/star-schema objects.
- `audit`: load metadata and reconciliation evidence.

Stage 2 focuses on the database, schemas, raw ingestion and reconciliation. Business transformations begin in Stage 3.

## Why raw columns are TEXT

The raw layer is intentionally source-preserving. It avoids mixing ingestion with business typing rules and makes it easier to distinguish:

- source problems
- parsing problems
- type-conversion problems
- business-rule problems

Typed columns and constraints will be introduced in the staging layer.

## Local setup

1. Install PostgreSQL and make sure the `psql` command is available.
2. Create a Python virtual environment.
3. Install `requirements.txt`.
4. Copy `.env.example` to `.env` and set the local PostgreSQL password.
5. Run `python .\scripts\load_postgres_raw.py`.
6. Reconcile counts using `sql/qa/01_raw_row_reconciliation.sql`.

## Stage 2 exit gate

- database `retail360` exists
- schemas `raw`, `staging`, `analytics`, `audit` exist
- all 14 validated source tables are loaded
- raw row counts reconcile exactly to source counts
- ingestion is repeatable without manual table editing
