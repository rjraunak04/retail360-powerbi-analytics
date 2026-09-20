# Retail360 — Recruiter-Friendly SQL Examples

These examples illustrate the business logic used in the analytics layer. They are simplified for discussion; the repository SQL scripts remain the implementation source of truth.

## 1. Revenue, cost and gross profit

```sql
SELECT
    SUM(sales_amount)        AS total_sales,
    SUM(total_product_cost)  AS total_product_cost,
    SUM(gross_profit)        AS gross_profit,
    SUM(order_quantity)      AS units_sold
FROM analytics.fact_sales;
```

## 2. Correct distinct order count across channels

Internet and Reseller order numbers can overlap, so the business key includes channel.

```sql
SELECT COUNT(*) AS distinct_orders
FROM (
    SELECT DISTINCT
        channel_key,
        sales_order_number
    FROM analytics.fact_sales
) q;
```

## 3. Channel reconciliation

```sql
SELECT
    c.channel_name,
    COUNT(*) AS sales_lines,
    SUM(f.sales_amount) AS sales
FROM analytics.fact_sales f
JOIN analytics.dim_channel c
  ON c.channel_key = f.channel_key
GROUP BY c.channel_name
ORDER BY sales DESC;
```

## 4. Weighted gross margin

```sql
SELECT
    SUM(gross_profit) / NULLIF(SUM(sales_amount), 0) AS gross_margin_pct
FROM analytics.fact_sales;
```

This intentionally does not average row-level margin percentages.

## 5. Top product categories

```sql
SELECT
    p.category_name,
    SUM(f.sales_amount) AS sales,
    SUM(f.gross_profit) AS gross_profit
FROM analytics.fact_sales f
JOIN analytics.dim_product p
  ON p.product_key = f.product_key
GROUP BY p.category_name
ORDER BY sales DESC;
```

## 6. Latest inventory snapshot

```sql
WITH latest AS (
    SELECT MAX(movement_date) AS latest_date
    FROM analytics.fact_inventory
)
SELECT
    i.movement_date,
    SUM(i.units_balance) AS current_inventory_units,
    SUM(i.inventory_value) AS current_inventory_value
FROM analytics.fact_inventory i
JOIN latest l
  ON i.movement_date = l.latest_date
GROUP BY i.movement_date;
```

## 7. Products below safety stock

```sql
WITH latest AS (
    SELECT MAX(movement_date) AS latest_date
    FROM analytics.fact_inventory
),
snapshot AS (
    SELECT
        product_key,
        SUM(units_balance) AS units_balance
    FROM analytics.fact_inventory i
    JOIN latest l
      ON i.movement_date = l.latest_date
    GROUP BY product_key
)
SELECT COUNT(*) AS products_below_safety_stock
FROM snapshot s
JOIN analytics.dim_product p
  ON p.product_key = s.product_key
WHERE s.units_balance < p.safety_stock_level;
```

## 8. Repeat customers

```sql
WITH customer_orders AS (
    SELECT
        customer_key,
        COUNT(DISTINCT (channel_key, sales_order_number)) AS orders
    FROM analytics.fact_sales
    WHERE customer_key <> 0
    GROUP BY customer_key
)
SELECT COUNT(*) AS repeat_customers
FROM customer_orders
WHERE orders > 1;
```

## 9. Territory-level RLS baseline

```sql
SELECT
    t.territory_group,
    COUNT(*) AS sales_lines,
    SUM(f.sales_amount) AS sales
FROM analytics.fact_sales f
JOIN analytics.dim_sales_territory t
  ON t.sales_territory_key = f.sales_territory_key
GROUP BY t.territory_group
ORDER BY sales DESC;
```

## 10. Data-quality reconciliation

```sql
SELECT
    COUNT(*) FILTER (WHERE product_key IS NULL) AS null_product_keys,
    COUNT(*) FILTER (WHERE order_date_key IS NULL) AS null_order_dates,
    COUNT(*) FILTER (WHERE order_quantity < 0) AS negative_quantity_rows
FROM analytics.fact_sales;
```

## Interview point

The SQL layer establishes stable row-level business definitions and analytical grain. DAX then handles filter-context-sensitive measures such as time intelligence, rank, selected-period contribution and role-playing dates.
