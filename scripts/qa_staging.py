from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Check:
    name: str
    sql: str
    expected: int


CHECKS = [
    Check("dim_currency row count", "SELECT count(*) FROM staging.dim_currency", 105),
    Check("dim_customer row count", "SELECT count(*) FROM staging.dim_customer", 18484),
    Check("dim_date row count", "SELECT count(*) FROM staging.dim_date", 3652),
    Check("dim_employee row count", "SELECT count(*) FROM staging.dim_employee", 296),
    Check("dim_geography row count", "SELECT count(*) FROM staging.dim_geography", 655),
    Check("dim_product row count", "SELECT count(*) FROM staging.dim_product", 606),
    Check("dim_promotion row count", "SELECT count(*) FROM staging.dim_promotion", 16),
    Check("dim_reseller row count", "SELECT count(*) FROM staging.dim_reseller", 701),
    Check("dim_sales_territory row count", "SELECT count(*) FROM staging.dim_sales_territory", 11),
    Check("internet sales row count", "SELECT count(*) FROM staging.fact_internet_sales", 60398),
    Check("reseller sales row count", "SELECT count(*) FROM staging.fact_reseller_sales", 60855),
    Check("unified sales row count", "SELECT count(*) FROM staging.fact_sales", 121253),
    Check("inventory row count", "SELECT count(*) FROM staging.fact_product_inventory", 776286),
    Check(
        "duplicate unified sales grain",
        """
        SELECT count(*)
        FROM (
            SELECT sales_line_id
            FROM staging.fact_sales
            GROUP BY sales_line_id
            HAVING count(*) > 1
        ) d
        """,
        0,
    ),
    Check(
        "null required sales grain fields",
        """
        SELECT count(*)
        FROM staging.fact_sales
        WHERE sales_line_id IS NULL
           OR product_key IS NULL
           OR order_date_key IS NULL
           OR sales_order_number IS NULL
           OR sales_order_line_number IS NULL
        """,
        0,
    ),
    Check(
        "sales product orphans",
        """
        SELECT count(*)
        FROM staging.fact_sales f
        LEFT JOIN staging.dim_product d USING (product_key)
        WHERE d.product_key IS NULL
        """,
        0,
    ),
    Check(
        "sales order-date orphans",
        """
        SELECT count(*)
        FROM staging.fact_sales f
        LEFT JOIN staging.dim_date d
          ON f.order_date_key = d.date_key
        WHERE d.date_key IS NULL
        """,
        0,
    ),
    Check(
        "internet customer orphans",
        """
        SELECT count(*)
        FROM staging.fact_internet_sales f
        LEFT JOIN staging.dim_customer d USING (customer_key)
        WHERE d.customer_key IS NULL
        """,
        0,
    ),
    Check(
        "reseller orphans",
        """
        SELECT count(*)
        FROM staging.fact_reseller_sales f
        LEFT JOIN staging.dim_reseller d USING (reseller_key)
        WHERE d.reseller_key IS NULL
        """,
        0,
    ),
    Check(
        "sales promotion orphans",
        """
        SELECT count(*)
        FROM staging.fact_sales f
        LEFT JOIN staging.dim_promotion d USING (promotion_key)
        WHERE d.promotion_key IS NULL
        """,
        0,
    ),
    Check(
        "sales currency orphans",
        """
        SELECT count(*)
        FROM staging.fact_sales f
        LEFT JOIN staging.dim_currency d USING (currency_key)
        WHERE d.currency_key IS NULL
        """,
        0,
    ),
    Check(
        "sales territory orphans",
        """
        SELECT count(*)
        FROM staging.fact_sales f
        LEFT JOIN staging.dim_sales_territory d USING (sales_territory_key)
        WHERE d.sales_territory_key IS NULL
        """,
        0,
    ),
    Check(
        "reseller employee orphans",
        """
        SELECT count(*)
        FROM staging.fact_reseller_sales f
        LEFT JOIN staging.dim_employee d USING (employee_key)
        WHERE d.employee_key IS NULL
        """,
        0,
    ),
    Check(
        "inventory product orphans",
        """
        SELECT count(*)
        FROM staging.fact_product_inventory f
        LEFT JOIN staging.dim_product d USING (product_key)
        WHERE d.product_key IS NULL
        """,
        0,
    ),
    Check(
        "inventory date orphans",
        """
        SELECT count(*)
        FROM staging.fact_product_inventory f
        LEFT JOIN staging.dim_date d
          ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
        """,
        0,
    ),
    Check(
        "invalid sales channel values",
        """
        SELECT count(*)
        FROM staging.fact_sales
        WHERE channel NOT IN ('Internet', 'Reseller')
           OR channel IS NULL
        """,
        0,
    ),
    Check(
        "gross profit formula mismatches",
        """
        SELECT count(*)
        FROM staging.fact_sales
        WHERE ABS(gross_profit - (sales_amount - total_product_cost)) > 0.0001
        """,
        0,
    ),
    Check(
        "inventory value formula mismatches",
        """
        SELECT count(*)
        FROM staging.fact_product_inventory
        WHERE ABS(inventory_value - (unit_cost * units_balance)) > 0.0001
        """,
        0,
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
    failures: list[tuple[str, int, int]] = []

    with psycopg.connect(**settings()) as conn:
        print("\nRetail360 Stage 3 staging QA")
        print("-" * 88)
        print(f"{'Check':48} {'Actual':>12} {'Expected':>12} {'Status':>10}")
        print("-" * 88)

        for check in CHECKS:
            actual = int(conn.execute(check.sql).fetchone()[0])
            status = "PASS" if actual == check.expected else "FAIL"
            print(f"{check.name:48} {actual:>12,} {check.expected:>12,} {status:>10}")
            if status == "FAIL":
                failures.append((check.name, actual, check.expected))

    print("-" * 88)
    if failures:
        details = "\n".join(
            f"- {name}: actual={actual}, expected={expected}"
            for name, actual, expected in failures
        )
        raise SystemExit(f"Stage 3 staging QA FAILED:\n{details}")

    print(f"Stage 3 staging QA PASSED: {len(CHECKS)}/{len(CHECKS)} checks.")


if __name__ == "__main__":
    main()
