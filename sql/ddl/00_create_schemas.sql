-- Retail360 Stage 2: PostgreSQL schema foundation
-- Run inside database: retail360

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

COMMENT ON SCHEMA raw IS 'Immutable landing layer for source-aligned AdventureWorksDW records.';
COMMENT ON SCHEMA staging IS 'Typed and cleaned transformation layer.';
COMMENT ON SCHEMA analytics IS 'Business-ready dimensional and reporting layer.';
COMMENT ON SCHEMA audit IS 'Load metadata, reconciliation results, and data-quality evidence.';
