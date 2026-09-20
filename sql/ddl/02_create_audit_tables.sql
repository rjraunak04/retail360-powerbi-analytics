-- Retail360 Stage 2: audit metadata

CREATE TABLE IF NOT EXISTS audit.load_run (
    load_run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    source_name text NOT NULL,
    status text NOT NULL CHECK (status IN ('RUNNING','SUCCESS','FAILED')),
    total_tables integer,
    total_rows bigint,
    notes text
);

CREATE TABLE IF NOT EXISTS audit.table_load (
    table_load_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    load_run_id bigint NOT NULL REFERENCES audit.load_run(load_run_id),
    table_name text NOT NULL,
    source_file text NOT NULL,
    loaded_rows bigint NOT NULL,
    nul_bytes_removed bigint NOT NULL DEFAULT 0,
    loaded_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE audit.table_load
ADD COLUMN IF NOT EXISTS nul_bytes_removed bigint NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS audit.row_reconciliation (
    reconciliation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    load_run_id bigint REFERENCES audit.load_run(load_run_id),
    table_name text NOT NULL,
    expected_rows bigint NOT NULL,
    actual_rows bigint NOT NULL,
    difference bigint NOT NULL,
    status text NOT NULL CHECK (status IN ('PASS','FAIL')),
    checked_at timestamptz NOT NULL DEFAULT now()
);
