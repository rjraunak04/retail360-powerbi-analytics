-- Retail360 Stage 3: human-readable staging QA summary

SELECT 'staging.fact_sales rows' AS metric, count(*)::numeric AS value
FROM staging.fact_sales
UNION ALL
SELECT 'internet sales rows', count(*) FROM staging.fact_internet_sales
UNION ALL
SELECT 'reseller sales rows', count(*) FROM staging.fact_reseller_sales
UNION ALL
SELECT 'inventory rows', count(*) FROM staging.fact_product_inventory
UNION ALL
SELECT 'total sales amount', ROUND(SUM(sales_amount), 2) FROM staging.fact_sales
UNION ALL
SELECT 'total gross profit', ROUND(SUM(gross_profit), 2) FROM staging.fact_sales
UNION ALL
SELECT 'total inventory value', ROUND(SUM(inventory_value), 2)
FROM staging.fact_product_inventory;
