from __future__ import annotations

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


def apply_ddl(conn: psycopg.Connection) -> None:
    for path in sorted(DDL_DIR.glob("*.sql")):
        print(f"Applying: {path.relative_to(ROOT)}")
        conn.execute(path.read_text(encoding="utf-8"))
    conn.commit()


def load_table(
    conn: psycopg.Connection,
    source_table: str,
) -> int:
    source_path = RAW_DIR / f"{source_table}.csv"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source file: {source_path}")

    table_name = snake(source_table)
    columns = [snake(column) for column in SCHEMAS[source_table]]

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
    load_dotenv(ROOT / ".env")
    dbname = os.getenv("PGDATABASE", "retail360")

    missing = [
        f"{table}.csv"
        for table in SCHEMAS
        if not (RAW_DIR / f"{table}.csv").exists()
    ]
    if missing:
        raise SystemExit(
            "Missing source files:\n- "
            + "\n- ".join(missing)
            + "\nRun: python .\\scripts\\download_adventureworks.py"
        )

    ensure_database(dbname)

    with psycopg.connect(**connection_settings(dbname)) as conn:
        apply_ddl(conn)

        load_run_id = conn.execute(
            """
            INSERT INTO audit.load_run (source_name, status)
            VALUES (%s, 'RUNNING')
            RETURNING load_run_id
            """,
            ("Microsoft AdventureWorksDW CSV",),
        ).fetchone()[0]
        conn.commit()

        total = 0
        table_count = 0

        try:
            print("\nLoading validated AdventureWorksDW source files...")
            for table in SCHEMAS:
                loaded = load_table(conn, table)
                table_count += 1
                total += loaded

                conn.execute(
                    """
                    INSERT INTO audit.table_load
                        (load_run_id, table_name, source_file, loaded_rows)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (load_run_id, snake(table), f"{table}.csv", loaded),
                )
                conn.commit()
                print(f"  {table:24} {loaded:>10,} rows")

            conn.execute(
                """
                UPDATE audit.load_run
                SET completed_at = now(),
                    status = 'SUCCESS',
                    total_tables = %s,
                    total_rows = %s
                WHERE load_run_id = %s
                """,
                (table_count, total, load_run_id),
            )
            conn.commit()

        except Exception as exc:
            conn.rollback()
            conn.execute(
                """
                UPDATE audit.load_run
                SET completed_at = now(),
                    status = 'FAILED',
                    total_tables = %s,
                    total_rows = %s,
                    notes = %s
                WHERE load_run_id = %s
                """,
                (table_count, total, str(exc)[:2000], load_run_id),
            )
            conn.commit()
            raise

        print(
            f"\nRaw load complete: {total:,} rows across "
            f"{table_count} tables. load_run_id={load_run_id}"
        )


if __name__ == "__main__":
    main()
