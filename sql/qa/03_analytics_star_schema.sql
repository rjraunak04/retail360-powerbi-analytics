-- Retail360 Stage 4: star-schema inspection queries

SELECT
    c.channel_name,
    COUNT(*) AS sales_lines,
    COUNT(DISTINCT f.sales_order_number) AS orders,
    SUM(f.order_quantity) AS units,
    ROUND(SUM(f.sales_amount), 2) AS sales,
    ROUND(SUM(f.gross_profit), 2) AS gross_profit,
    ROUND(
        SUM(f.gross_profit) / NULLIF(SUM(f.sales_amount), 0) * 100,
        2
    ) AS gross_margin_pct
FROM analytics.fact_sales f
JOIN analytics.dim_channel c USING (channel_key)
GROUP BY c.channel_name
ORDER BY c.channel_name;

SELECT
    COUNT(*) AS inventory_rows,
    ROUND(SUM(inventory_value), 2) AS snapshot_inventory_value,
    SUM(units_balance) AS snapshot_units_balance
FROM analytics.fact_inventory;
