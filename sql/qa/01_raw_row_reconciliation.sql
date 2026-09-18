-- Retail360 Stage 2: raw-layer reconciliation
-- Expected counts from the validated source files.

WITH expected(table_name, expected_rows) AS (
    VALUES
        ('dim_currency', 105::bigint),
        ('dim_customer', 18484),
        ('dim_date', 3652),
        ('dim_employee', 296),
        ('dim_geography', 655),
        ('dim_product', 606),
        ('dim_product_category', 4),
        ('dim_product_subcategory', 37),
        ('dim_promotion', 16),
        ('dim_reseller', 701),
        ('dim_sales_territory', 11),
        ('fact_internet_sales', 60398),
        ('fact_reseller_sales', 60855),
        ('fact_product_inventory', 776286)
),
actual AS (
    SELECT 'dim_currency' table_name, count(*)::bigint actual_rows FROM raw.dim_currency
    UNION ALL SELECT 'dim_customer', count(*) FROM raw.dim_customer
    UNION ALL SELECT 'dim_date', count(*) FROM raw.dim_date
    UNION ALL SELECT 'dim_employee', count(*) FROM raw.dim_employee
    UNION ALL SELECT 'dim_geography', count(*) FROM raw.dim_geography
    UNION ALL SELECT 'dim_product', count(*) FROM raw.dim_product
    UNION ALL SELECT 'dim_product_category', count(*) FROM raw.dim_product_category
    UNION ALL SELECT 'dim_product_subcategory', count(*) FROM raw.dim_product_subcategory
    UNION ALL SELECT 'dim_promotion', count(*) FROM raw.dim_promotion
    UNION ALL SELECT 'dim_reseller', count(*) FROM raw.dim_reseller
    UNION ALL SELECT 'dim_sales_territory', count(*) FROM raw.dim_sales_territory
    UNION ALL SELECT 'fact_internet_sales', count(*) FROM raw.fact_internet_sales
    UNION ALL SELECT 'fact_reseller_sales', count(*) FROM raw.fact_reseller_sales
    UNION ALL SELECT 'fact_product_inventory', count(*) FROM raw.fact_product_inventory
)
SELECT
    e.table_name,
    e.expected_rows,
    a.actual_rows,
    a.actual_rows - e.expected_rows AS difference,
    CASE WHEN a.actual_rows = e.expected_rows THEN 'PASS' ELSE 'FAIL' END AS status
FROM expected e
JOIN actual a USING (table_name)
ORDER BY e.table_name;
