from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

EXPECTED = {
    "dim_currency": 105,
    "dim_customer": 18484,
    "dim_date": 3652,
    "dim_employee": 296,
    "dim_geography": 655,
    "dim_product": 606,
    "dim_product_category": 4,
    "dim_product_subcategory": 37,
    "dim_promotion": 16,
    "dim_reseller": 701,
    "dim_sales_territory": 11,
    "fact_internet_sales": 60398,
    "fact_reseller_sales": 60855,
    "fact_product_inventory": 776286,
}


def settings() -> dict[str, object]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD") or None,
        "dbname": os.getenv("PGDATABASE", "retail360"),
    }


def main() -> None:
    rows: list[tuple[str, int, int, int, str]] = []
    failures = 0

    with psycopg.connect(**settings()) as conn:
        run_row = conn.execute(
            """
            SELECT load_run_id, status, total_tables, total_rows
            FROM audit.load_run
            ORDER BY load_run_id DESC
            LIMIT 1
            """
        ).fetchone()

        if not run_row:
            raise SystemExit("No audit.load_run record found.")

        load_run_id, load_status, total_tables, total_rows = run_row
        expected_total_rows = sum(EXPECTED.values())

        if load_status != "SUCCESS":
            raise SystemExit(f"Latest load run is not SUCCESS: {load_status}")
        if int(total_tables or 0) != len(EXPECTED):
            raise SystemExit(
                f"Audit table count mismatch: expected {len(EXPECTED)}, got {total_tables}"
            )
        if int(total_rows or 0) != expected_total_rows:
            raise SystemExit(
                f"Audit total row mismatch: expected {expected_total_rows}, got {total_rows}"
            )

        table_load_count = int(
            conn.execute(
                "SELECT count(*) FROM audit.table_load WHERE load_run_id = %s",
                (load_run_id,),
            ).fetchone()[0]
        )
        if table_load_count != len(EXPECTED):
            raise SystemExit(
                f"Audit table_load mismatch: expected {len(EXPECTED)}, got {table_load_count}"
            )

        conn.execute("DELETE FROM audit.row_reconciliation WHERE load_run_id IS NOT DISTINCT FROM %s", (load_run_id,))

        for table_name, expected in EXPECTED.items():
            query = sql.SQL("SELECT count(*) FROM raw.{}").format(sql.Identifier(table_name))
            actual = int(conn.execute(query).fetchone()[0])
            difference = actual - expected
            status = "PASS" if difference == 0 else "FAIL"
            if status == "FAIL":
                failures += 1

            conn.execute(
                """
                INSERT INTO audit.row_reconciliation
                    (load_run_id, table_name, expected_rows, actual_rows, difference, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (load_run_id, table_name, expected, actual, difference, status),
            )
            rows.append((table_name, expected, actual, difference, status))

        conn.commit()

    print("\nRetail360 PostgreSQL raw reconciliation")
    print("-" * 86)
    print(f"{'Table':28} {'Expected':>10} {'Actual':>10} {'Diff':>10} {'Status':>8}")
    print("-" * 86)
    for table_name, expected, actual, difference, status in rows:
        print(f"{table_name:28} {expected:>10,} {actual:>10,} {difference:>10,} {status:>8}")
    print("-" * 86)

    if failures:
        raise SystemExit(f"Raw reconciliation FAILED: {failures} table(s) mismatched.")

    print(
        "Raw reconciliation PASSED: 14/14 tables match validated source counts "
        "and the latest audited load is complete."
    )


if __name__ == "__main__":
    main()
