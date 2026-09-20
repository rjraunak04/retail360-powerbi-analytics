from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
BASELINE = RUNTIME / "stage8-rls-baseline.json"
load_dotenv(ROOT / ".env")

REGIONS = ("North America", "Europe", "Pacific")


def dec(value) -> Decimal:
    return Decimal(str(value or 0))


def main() -> None:
    conn = psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD") or None,
        dbname=os.getenv("PGDATABASE", "retail360"),
    )

    checks: list[tuple[str, object, object, bool]] = []

    with conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                COUNT(*)::bigint AS fact_sales_rows,
                SUM(sales_amount)::numeric AS total_sales,
                COUNT(DISTINCT (channel_key, sales_order_number))::bigint AS orders,
                COUNT(*) FILTER (WHERE order_quantity <= 0)::bigint AS nonpositive_qty,
                COUNT(*) FILTER (WHERE sales_amount < 0)::bigint AS negative_sales,
                COUNT(*) FILTER (
                    WHERE ABS(gross_profit - (sales_amount - total_product_cost)) > 0.0001
                )::bigint AS gross_profit_mismatch,
                COUNT(*) FILTER (
                    WHERE sales_amount <> 0
                      AND ABS(gross_margin_pct - (gross_profit / sales_amount)) > 0.000001
                )::bigint AS gross_margin_mismatch,
                COUNT(*) FILTER (WHERE due_date < order_date)::bigint AS due_before_order,
                COUNT(*) FILTER (
                    WHERE ship_date IS NOT NULL AND ship_date < order_date
                )::bigint AS ship_before_order,
                COUNT(*) FILTER (
                    WHERE channel_key = 1 AND (reseller_key <> 0 OR employee_key <> 0)
                )::bigint AS internet_applicability_errors,
                COUNT(*) FILTER (
                    WHERE channel_key = 2 AND customer_key <> 0
                )::bigint AS reseller_applicability_errors,
                COUNT(DISTINCT currency_key)::bigint AS currency_keys
            FROM analytics.fact_sales
            """
        )
        sales = dict(zip([d.name for d in cur.description], cur.fetchone()))

        cur.execute(
            """
            SELECT COUNT(*)::bigint
            FROM (
                SELECT channel_key, sales_order_number, sales_order_line_number
                FROM analytics.fact_sales
                GROUP BY 1,2,3
                HAVING COUNT(*) > 1
            ) d
            """
        )
        duplicate_sales_grains = int(cur.fetchone()[0])

        cur.execute(
            """
            SELECT
                COUNT(*)::bigint AS fact_inventory_rows,
                MIN(movement_date)::date AS min_inventory_date,
                MAX(movement_date)::date AS max_inventory_date,
                COUNT(*) FILTER (WHERE units_balance < 0)::bigint AS negative_balance_rows,
                COUNT(*) FILTER (WHERE inventory_value < 0)::bigint AS negative_value_rows
            FROM analytics.fact_inventory
            """
        )
        inventory = dict(zip([d.name for d in cur.description], cur.fetchone()))

        cur.execute(
            """
            SELECT COUNT(*)::bigint
            FROM (
                SELECT product_key, date_key
                FROM analytics.fact_inventory
                GROUP BY 1,2
                HAVING COUNT(*) > 1
            ) d
            """
        )
        duplicate_inventory_grains = int(cur.fetchone()[0])

        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'analytics'
                  AND table_name = 'fact_inventory'
                  AND column_name = 'sales_territory_key'
            )
            """
        )
        inventory_has_territory = bool(cur.fetchone()[0])

        cur.execute(
            """
            SELECT
                COALESCE(st.territory_group, 'Unknown') AS territory_group,
                COUNT(*)::bigint AS sales_rows,
                SUM(fs.sales_amount)::numeric AS total_sales,
                COUNT(DISTINCT (fs.channel_key, fs.sales_order_number))::bigint AS orders
            FROM analytics.fact_sales fs
            JOIN analytics.dim_sales_territory st
              ON st.sales_territory_key = fs.sales_territory_key
            GROUP BY COALESCE(st.territory_group, 'Unknown')
            ORDER BY 1
            """
        )
        territory_rows = {
            str(row[0]): {
                "sales_rows": int(row[1]),
                "total_sales": str(row[2]),
                "orders": int(row[3]),
            }
            for row in cur.fetchall()
        }

        cur.execute(
            """
            SELECT COUNT(*)::bigint
            FROM analytics.fact_sales fs
            LEFT JOIN analytics.dim_product p ON p.product_key = fs.product_key
            LEFT JOIN analytics.dim_channel c ON c.channel_key = fs.channel_key
            LEFT JOIN analytics.dim_date od ON od.date_key = fs.order_date_key
            LEFT JOIN analytics.dim_date dd ON dd.date_key = fs.due_date_key
            LEFT JOIN analytics.dim_sales_territory st
              ON st.sales_territory_key = fs.sales_territory_key
            WHERE p.product_key IS NULL
               OR c.channel_key IS NULL
               OR od.date_key IS NULL
               OR dd.date_key IS NULL
               OR st.sales_territory_key IS NULL
            """
        )
        broken_sales_fk = int(cur.fetchone()[0])

    checks.extend(
        [
            ("FactSales row count", int(sales["fact_sales_rows"]), 121253, int(sales["fact_sales_rows"]) == 121253),
            ("FactInventory row count", int(inventory["fact_inventory_rows"]), 776286, int(inventory["fact_inventory_rows"]) == 776286),
            ("Duplicate sales grains", duplicate_sales_grains, 0, duplicate_sales_grains == 0),
            ("Duplicate inventory grains", duplicate_inventory_grains, 0, duplicate_inventory_grains == 0),
            ("Broken core sales FKs", broken_sales_fk, 0, broken_sales_fk == 0),
            ("Nonpositive sales quantity", int(sales["nonpositive_qty"]), 0, int(sales["nonpositive_qty"]) == 0),
            ("Negative sales amount", int(sales["negative_sales"]), 0, int(sales["negative_sales"]) == 0),
            ("Gross-profit arithmetic mismatch", int(sales["gross_profit_mismatch"]), 0, int(sales["gross_profit_mismatch"]) == 0),
            ("Gross-margin arithmetic mismatch", int(sales["gross_margin_mismatch"]), 0, int(sales["gross_margin_mismatch"]) == 0),
            ("Due date before order date", int(sales["due_before_order"]), 0, int(sales["due_before_order"]) == 0),
            ("Ship date before order date", int(sales["ship_before_order"]), 0, int(sales["ship_before_order"]) == 0),
            ("Internet applicability errors", int(sales["internet_applicability_errors"]), 0, int(sales["internet_applicability_errors"]) == 0),
            ("Reseller applicability errors", int(sales["reseller_applicability_errors"]), 0, int(sales["reseller_applicability_errors"]) == 0),
            ("Inventory territory column absent", inventory_has_territory, False, not inventory_has_territory),
            ("Inventory date range valid", str(inventory["max_inventory_date"]), "after min date", inventory["max_inventory_date"] > inventory["min_inventory_date"]),
            ("Negative inventory balance rows", int(inventory["negative_balance_rows"]), 0, int(inventory["negative_balance_rows"]) == 0),
            ("Negative inventory value rows", int(inventory["negative_value_rows"]), 0, int(inventory["negative_value_rows"]) == 0),
        ]
    )

    missing_regions = [r for r in REGIONS if r not in territory_rows]
    regional_sales = sum(dec(territory_rows.get(r, {}).get("total_sales")) for r in REGIONS)
    total_sales = dec(sales["total_sales"])
    checks.append(("Required RLS regions present", len(missing_regions), 0, not missing_regions))
    checks.append(("Regional sales reconcile", regional_sales, total_sales, abs(regional_sales - total_sales) <= Decimal("0.0001")))

    print("Retail360 Stage 8 enterprise SQL / edge-case QA")
    print("-" * 100)
    print(f"{'Check':42} {'Actual':>22} {'Expected':>22} {'Status':>8}")
    print("-" * 100)
    failures = 0
    for name, actual, expected, passed in checks:
        status = "PASS" if passed else "FAIL"
        failures += 0 if passed else 1
        print(f"{name:42} {str(actual):>22} {str(expected):>22} {status:>8}")
    print("-" * 100)
    print(f"Distinct currency keys observed: {sales['currency_keys']}")
    for region in REGIONS:
        print(f"RLS baseline {region:15}: {territory_rows.get(region)}")

    RUNTIME.mkdir(parents=True, exist_ok=True)
    baseline = {
        "global": {
            "sales_rows": int(sales["fact_sales_rows"]),
            "total_sales": str(sales["total_sales"]),
            "orders": int(sales["orders"]),
        },
        "territory_groups": {region: territory_rows.get(region) for region in REGIONS},
        "inventory": {
            "rows": int(inventory["fact_inventory_rows"]),
            "min_date": str(inventory["min_inventory_date"]),
            "max_date": str(inventory["max_inventory_date"]),
            "territory_key_present": inventory_has_territory,
        },
    }
    BASELINE.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(f"Stage 8 RLS baseline: {BASELINE}")

    if failures:
        raise SystemExit(f"Stage 8 enterprise SQL QA FAILED: {failures} check(s) failed.")

    print(f"Stage 8 enterprise SQL QA PASSED: {len(checks)}/{len(checks)} checks.")


if __name__ == "__main__":
    main()
