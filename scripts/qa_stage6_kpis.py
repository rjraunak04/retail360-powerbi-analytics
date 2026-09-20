from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def d(value) -> Decimal:
    return Decimal(str(value))


def close(a: Decimal, b: Decimal, tol: Decimal = Decimal("0.0001")) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    conn = psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD") or None,
        dbname=os.getenv("PGDATABASE", "retail360"),
    )

    with conn, conn.cursor() as cur:
        cur.execute(
            """
            WITH base AS (
                SELECT
                    SUM(sales_amount)::numeric AS total_sales,
                    SUM(total_product_cost)::numeric AS total_cost,
                    SUM(gross_profit)::numeric AS gross_profit,
                    SUM(order_quantity)::bigint AS units_sold,
                    COUNT(DISTINCT (channel_key, sales_order_number))::bigint AS distinct_orders,
                    COUNT(DISTINCT customer_key) FILTER (WHERE customer_key <> 0)::bigint AS customers,
                    COUNT(DISTINCT reseller_key) FILTER (WHERE reseller_key <> 0)::bigint AS resellers,
                    COUNT(DISTINCT product_key) FILTER (WHERE product_key <> 0)::bigint AS products_sold,
                    SUM(sales_amount) FILTER (WHERE channel_key = 1)::numeric AS internet_sales,
                    SUM(sales_amount) FILTER (WHERE channel_key = 2)::numeric AS reseller_sales,
                    SUM(sales_amount) FILTER (WHERE discount_amount > 0)::numeric AS discounted_sales
                FROM analytics.fact_sales
            ),
            repeat_customers AS (
                SELECT COUNT(*)::bigint AS repeat_customers
                FROM (
                    SELECT customer_key
                    FROM analytics.fact_sales
                    WHERE customer_key <> 0
                    GROUP BY customer_key
                    HAVING COUNT(DISTINCT (channel_key, sales_order_number)) > 1
                ) x
            ),
            latest AS (
                SELECT MAX(movement_date)::date AS latest_inventory_date
                FROM analytics.fact_inventory
            ),
            inv AS (
                SELECT
                    SUM(fi.inventory_value)::numeric AS current_inventory_value,
                    SUM(fi.units_balance)::bigint AS current_inventory_units,
                    COUNT(DISTINCT fi.product_key) FILTER (WHERE fi.product_key <> 0)::bigint AS products_with_inventory,
                    COUNT(DISTINCT fi.product_key) FILTER (
                        WHERE fi.product_key <> 0
                          AND fi.units_balance < dp.safety_stock_level
                    )::bigint AS products_below_safety_stock,
                    COUNT(DISTINCT fi.product_key) FILTER (
                        WHERE fi.product_key <> 0
                          AND fi.units_balance < dp.reorder_point
                    )::bigint AS products_below_reorder_point
                FROM analytics.fact_inventory fi
                JOIN latest l ON fi.movement_date = l.latest_inventory_date
                JOIN analytics.dim_product dp ON dp.product_key = fi.product_key
            ),
            yearly AS (
                SELECT
                    SUM(sales_amount) FILTER (WHERE EXTRACT(YEAR FROM order_date) = 2013)::numeric AS sales_2013,
                    SUM(sales_amount) FILTER (WHERE EXTRACT(YEAR FROM order_date) = 2014)::numeric AS sales_2014,
                    SUM(sales_amount) FILTER (WHERE EXTRACT(YEAR FROM due_date) = 2013)::numeric AS due_sales_2013,
                    SUM(sales_amount) FILTER (WHERE EXTRACT(YEAR FROM ship_date) = 2013)::numeric AS ship_sales_2013,
                    SUM(gross_profit) FILTER (WHERE EXTRACT(YEAR FROM order_date) = 2013)::numeric AS profit_2013,
                    SUM(gross_profit) FILTER (WHERE EXTRACT(YEAR FROM order_date) = 2014)::numeric AS profit_2014
                FROM analytics.fact_sales
            )
            SELECT
                b.total_sales, b.total_cost, b.gross_profit, b.units_sold, b.distinct_orders,
                b.customers, r.repeat_customers, b.resellers, b.products_sold,
                b.internet_sales, b.reseller_sales, b.discounted_sales,
                l.latest_inventory_date, i.current_inventory_value, i.current_inventory_units,
                i.products_with_inventory, i.products_below_safety_stock, i.products_below_reorder_point,
                y.sales_2013, y.sales_2014, y.due_sales_2013, y.ship_sales_2013,
                y.profit_2013, y.profit_2014
            FROM base b
            CROSS JOIN repeat_customers r
            CROSS JOIN latest l
            CROSS JOIN inv i
            CROSS JOIN yearly y
            """
        )
        row = cur.fetchone()
        cols = [desc.name for desc in cur.description]
        metrics = dict(zip(cols, row))

    expected = {
        "total_sales": d("109809274.2030"),
        "total_cost": d("97257907.9547"),
        "gross_profit": d("12551366.2483"),
        "units_sold": 274776,
        "distinct_orders": 31455,
    }

    failures: list[str] = []
    for key in ("total_sales", "total_cost", "gross_profit"):
        if not close(d(metrics[key]), expected[key]):
            failures.append(f"{key}: {metrics[key]} != {expected[key]}")
    for key in ("units_sold", "distinct_orders"):
        if int(metrics[key]) != expected[key]:
            failures.append(f"{key}: {metrics[key]} != {expected[key]}")

    if not close(d(metrics["internet_sales"]) + d(metrics["reseller_sales"]), d(metrics["total_sales"])):
        failures.append("channel sales do not reconcile to total sales")
    if int(metrics["repeat_customers"]) > int(metrics["customers"]):
        failures.append("repeat customers exceed customers")
    if int(metrics["products_below_reorder_point"]) > int(metrics["products_with_inventory"]):
        failures.append("reorder-risk products exceed products with inventory")
    if int(metrics["products_below_safety_stock"]) > int(metrics["products_with_inventory"]):
        failures.append("safety-stock-risk products exceed products with inventory")
    if d(metrics["current_inventory_value"]) <= 0:
        failures.append("current inventory value is not positive")
    if int(metrics["current_inventory_units"]) <= 0:
        failures.append("current inventory units are not positive")

    print("Retail360 Stage 6 SQL KPI benchmark")
    print("-" * 88)
    for key in cols:
        print(f"{key:36} {metrics[key]}")
    print("-" * 88)

    if failures:
        print("Stage 6 SQL benchmark FAILED:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Stage 6 SQL KPI benchmark PASSED.")


if __name__ == "__main__":
    main()
