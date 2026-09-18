from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from psycopg import sql

from validate_source_integrity import SCHEMAS

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "adventureworks"
DDL_DIR = ROOT / "sql" / "ddl"


def snake(name: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    return value.lower()


def connection_settings(database: str | None = None) -> dict[str, object]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD") or None,
        "dbname": database or os.getenv("PGDATABASE", "retail360"),
    }


def ensure_database(dbname: str) -> None:
    settings = connection_settings("postgres")
    with psycopg.connect(**settings, autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,),
        ).fetchone()
        if exists:
            print(f"Database already exists: {dbname}")
            return

        print(f"Creating database: {dbname}")
        conn.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname))
        )


def run_sql_file(conn: psycopg.Connection, path: Path) -> None:
    print(f"Applying: {path.relative_to(ROOT)}")
    conn.execute(path.read_text(encoding="utf-8"))


def load_table(
    conn: psycopg.Connection,
    source_table: str,
    *,
    truncate: bool,
) -> int:
    source_path = RAW_DIR / f"{source_table}.csv"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source file: {source_path}")

    table_name = snake(source_table)
    columns = [snake(column) for column in SCHEMAS[source_table]]

    if truncate:
        conn.execute(
            sql.SQL("TRUNCATE TABLE raw.{}").format(sql.Identifier(table_name))
        )

    copy_columns = columns + ["_source_file", "_source_row_number"]
    copy_stmt = sql.SQL("COPY raw.{} ({}) FROM STDIN").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, copy_columns)),
    )

    loaded = 0
    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="|")
        with conn.cursor().copy(copy_stmt) as copy:
            for row_number, row in enumerate(reader, start=1):
                if len(row) != len(columns):
                    raise ValueError(
                        f"{source_table} row {row_number}: expected "
                        f"{len(columns)} fields, found {len(row)}"
                    )
                copy.write_row(row + [source_path.name, row_number])
                loaded += 1

    return loaded


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Retail360 PostgreSQL raw layer and load validated source data."
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Append instead of truncating raw tables before load.",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    dbname = os.getenv("PGDATABASE", "retail360")

    ensure_database(dbname)

    with psycopg.connect(**connection_settings(dbname)) as conn:
        run_sql_file(conn, DDL_DIR / "00_create_schemas.sql")
        run_sql_file(conn, DDL_DIR / "01_create_raw_tables.sql")
        conn.commit()

        print("\nLoading validated AdventureWorksDW source files...")
        total = 0
        for table in SCHEMAS:
            loaded = load_table(conn, table, truncate=not args.no_truncate)
            conn.commit()
            total += loaded
            print(f"  {table:24} {loaded:>10,} rows")

        print(f"\nRaw load complete: {total:,} rows across {len(SCHEMAS)} tables.")


if __name__ == "__main__":
    main()
