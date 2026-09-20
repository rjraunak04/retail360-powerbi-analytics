from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class CountCheck:
    name: str
    sql: str
    expected: int


COUNT_CHECKS = [
    CountCheck("fact_sales row count", "SELECT count(*) FROM analytics.fact_sales", 121253),
    CountCheck("fact_inventory row count", "SELECT count(*) FROM analytics.fact_inventory", 776286),
    CountCheck(
        "Internet channel row count",
        """
        SELECT count(*)
        FROM analytics.fact_sales f
        JOIN analytics.dim_channel c USING (channel_key)
        WHERE c.channel_name = 'Internet'
        """,
        60398,
    ),
    CountCheck(
        "Reseller channel row count",
        """
        SELECT count(*)
        FROM analytics.fact_sales f
        JOIN analytics.dim_channel c USING (channel_key)
        WHERE c.channel_name = 'Reseller'
        """,
        60855,
    ),
    CountCheck(
        "duplicate sales-line grain",
        """
        SELECT count(*)
        FROM (
            SELECT sales_line_id
            FROM analytics.fact_sales
            GROUP BY sales_line_id
            HAVING count(*) > 1
        ) x
        """,
        0,
    ),
    CountCheck(
        "duplicate inventory grain",
        """
        SELECT count(*)
        FROM (
            SELECT product_key, date_key
            FROM analytics.fact_inventory
            GROUP BY product_key, date_key
            HAVING count(*) > 1
        ) x
        """,
        0,
    ),
    CountCheck(
        "null sales foreign keys",
        """
        SELECT count(*)
        FROM analytics.fact_sales
        WHERE channel_key IS NULL
           OR product_key IS NULL
           OR order_date_key IS NULL
           OR due_date_key IS NULL
           OR ship_date_key IS NULL
           OR customer_key IS NULL
           OR reseller_key IS NULL
           OR employee_key IS NULL
           OR promotion_key IS NULL
           OR currency_key IS NULL
           OR sales_territory_key IS NULL
           OR geography_key IS NULL
        """,
        0,
    ),
    CountCheck(
        "invalid channel keys",
        "SELECT count(*) FROM analytics.fact_sales WHERE channel_key NOT IN (1,2)",
        0,
    ),
    CountCheck(
        "Internet rows with reseller/employee applicability error",
        """
        SELECT count(*)
        FROM analytics.fact_sales
        WHERE channel_key = 1
          AND (reseller_key <> 0 OR employee_key <> 0 OR customer_key = 0)
        """,
        0,
    ),
    CountCheck(
        "Reseller rows with customer applicability error",
        """
        SELECT count(*)
        FROM analytics.fact_sales
        WHERE channel_key = 2
          AND (customer_key <> 0 OR reseller_key = 0 OR employee_key = 0)
        """,
        0,
    ),
    CountCheck(
        "missing unknown customer member",
        "SELECT count(*) FROM analytics.dim_customer WHERE customer_key = 0",
        1,
    ),
    CountCheck(
        "missing unknown reseller member",
        "SELECT count(*) FROM analytics.dim_reseller WHERE reseller_key = 0",
        1,
    ),
    CountCheck(
        "missing unknown employee member",
        "SELECT count(*) FROM analytics.dim_employee WHERE employee_key = 0",
        1,
    ),
    CountCheck(
        "missing unknown geography member",
        "SELECT count(*) FROM analytics.dim_geography WHERE geography_key = 0",
        1,
    ),
    CountCheck(
        "blank dates in analytics dim_date",
        "SELECT count(*) FROM analytics.dim_date WHERE date IS NULL",
        0,
    ),
    CountCheck(
        "fact rows using unknown date key 0",
        """
        SELECT
            (SELECT count(*) FROM analytics.fact_sales
             WHERE order_date_key = 0 OR due_date_key = 0 OR ship_date_key = 0)
          + (SELECT count(*) FROM analytics.fact_inventory WHERE date_key = 0)
        """,
        0,
    ),
    CountCheck(
        "foreign-key constraint count",
        """
        SELECT count(*)
        FROM pg_constraint
        WHERE connamespace = 'analytics'::regnamespace
          AND contype = 'f'
          AND conrelid IN (
              'analytics.fact_sales'::regclass,
              'analytics.fact_inventory'::regclass
          )
        """,
        14,
    ),
]


VALUE_CHECKS = [
    (
        "sales amount preservation",
        "SELECT COALESCE(SUM(sales_amount),0) FROM staging.fact_sales",
        "SELECT COALESCE(SUM(sales_amount),0) FROM analytics.fact_sales",
    ),
    (
        "total product cost preservation",
        "SELECT COALESCE(SUM(total_product_cost),0) FROM staging.fact_sales",
        "SELECT COALESCE(SUM(total_product_cost),0) FROM analytics.fact_sales",
    ),
    (
        "gross profit preservation",
        "SELECT COALESCE(SUM(gross_profit),0) FROM staging.fact_sales",
        "SELECT COALESCE(SUM(gross_profit),0) FROM analytics.fact_sales",
    ),
    (
        "sales units preservation",
        "SELECT COALESCE(SUM(order_quantity),0) FROM staging.fact_sales",
        "SELECT COALESCE(SUM(order_quantity),0) FROM analytics.fact_sales",
    ),
    (
        "inventory value preservation",
        "SELECT COALESCE(SUM(inventory_value),0) FROM staging.fact_product_inventory",
        "SELECT COALESCE(SUM(inventory_value),0) FROM analytics.fact_inventory",
    ),
    (
        "inventory units balance preservation",
        "SELECT COALESCE(SUM(units_balance),0) FROM staging.fact_product_inventory",
        "SELECT COALESCE(SUM(units_balance),0) FROM analytics.fact_inventory",
    ),
]


def settings() -> dict[str, object]:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD") or None,
        "dbname": os.getenv("PGDATABASE", "retail360"),
    }


def main() -> None:
    failures: list[str] = []

    with psycopg.connect(**settings()) as conn:
        print("\nRetail360 Stage 4 analytics star-schema QA")
        print("-" * 100)
        print(f"{'Count check':55} {'Actual':>12} {'Expected':>12} {'Status':>10}")
        print("-" * 100)

        for check in COUNT_CHECKS:
            actual = int(conn.execute(check.sql).fetchone()[0])
            status = "PASS" if actual == check.expected else "FAIL"
            print(f"{check.name:55} {actual:>12,} {check.expected:>12,} {status:>10}")
            if status == "FAIL":
                failures.append(
                    f"{check.name}: actual={actual}, expected={check.expected}"
                )

        print("\nMetric preservation checks")
        print("-" * 100)
        for name, source_sql, target_sql in VALUE_CHECKS:
            source = Decimal(conn.execute(source_sql).fetchone()[0])
            target = Decimal(conn.execute(target_sql).fetchone()[0])
            difference = target - source
            status = "PASS" if abs(difference) <= Decimal("0.0001") else "FAIL"
            print(
                f"{name:55} source={source} target={target} "
                f"diff={difference} {status}"
            )
            if status == "FAIL":
                failures.append(
                    f"{name}: source={source}, target={target}, diff={difference}"
                )

        print("\nAnalytics KPI baseline")
        print("-" * 100)
        metrics = {
            "Total Sales": "SELECT SUM(sales_amount) FROM analytics.fact_sales",
            "Total Product Cost": "SELECT SUM(total_product_cost) FROM analytics.fact_sales",
            "Gross Profit": "SELECT SUM(gross_profit) FROM analytics.fact_sales",
            "Units Sold": "SELECT SUM(order_quantity) FROM analytics.fact_sales",
            "Distinct Orders": "SELECT COUNT(DISTINCT channel_key::text || '|' || sales_order_number) FROM analytics.fact_sales",
            "Inventory Value (all snapshots)": "SELECT SUM(inventory_value) FROM analytics.fact_inventory",
        }
        for name, query in metrics.items():
            value = conn.execute(query).fetchone()[0]
            print(f"{name:35} {value}")

    print("-" * 100)
    if failures:
        raise SystemExit("Stage 4 QA FAILED:\n- " + "\n- ".join(failures))

    print(
        f"Stage 4 analytics QA PASSED: {len(COUNT_CHECKS)} count/integrity checks "
        f"+ {len(VALUE_CHECKS)} metric-preservation checks."
    )


if __name__ == "__main__":
    main()
