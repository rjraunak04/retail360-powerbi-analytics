-- Retail360 Stage 3: typed business facts and channel harmonisation

CREATE OR REPLACE VIEW staging.fact_internet_sales AS
SELECT
    'Internet'::text AS channel,
    CONCAT('I|', sales_order_number, '|', sales_order_line_number) AS sales_line_id,
    NULLIF(BTRIM(product_key), '')::integer AS product_key,
    NULLIF(BTRIM(order_date_key), '')::integer AS order_date_key,
    NULLIF(BTRIM(due_date_key), '')::integer AS due_date_key,
    NULLIF(BTRIM(ship_date_key), '')::integer AS ship_date_key,
    NULLIF(BTRIM(customer_key), '')::integer AS customer_key,
    NULL::integer AS reseller_key,
    NULL::integer AS employee_key,
    NULLIF(BTRIM(promotion_key), '')::integer AS promotion_key,
    NULLIF(BTRIM(currency_key), '')::integer AS currency_key,
    NULLIF(BTRIM(sales_territory_key), '')::integer AS sales_territory_key,
    NULLIF(BTRIM(sales_order_number), '') AS sales_order_number,
    NULLIF(BTRIM(sales_order_line_number), '')::smallint AS sales_order_line_number,
    NULLIF(BTRIM(revision_number), '')::smallint AS revision_number,
    NULLIF(BTRIM(order_quantity), '')::integer AS order_quantity,
    NULLIF(BTRIM(unit_price), '')::numeric(19,4) AS unit_price,
    NULLIF(BTRIM(extended_amount), '')::numeric(19,4) AS extended_amount,
    NULLIF(BTRIM(unit_price_discount_pct), '')::numeric(12,6) AS unit_price_discount_pct,
    NULLIF(BTRIM(discount_amount), '')::numeric(19,4) AS discount_amount,
    NULLIF(BTRIM(product_standard_cost), '')::numeric(19,4) AS product_standard_cost,
    NULLIF(BTRIM(total_product_cost), '')::numeric(19,4) AS total_product_cost,
    NULLIF(BTRIM(sales_amount), '')::numeric(19,4) AS sales_amount,
    NULLIF(BTRIM(tax_amt), '')::numeric(19,4) AS tax_amount,
    NULLIF(BTRIM(freight), '')::numeric(19,4) AS freight,
    (
        NULLIF(BTRIM(sales_amount), '')::numeric(19,4)
        - NULLIF(BTRIM(total_product_cost), '')::numeric(19,4)
    ) AS gross_profit,
    (
        NULLIF(BTRIM(sales_amount), '')::numeric
        - NULLIF(BTRIM(total_product_cost), '')::numeric
    ) / NULLIF(NULLIF(BTRIM(sales_amount), '')::numeric, 0) AS gross_margin_pct,
    NULLIF(BTRIM(order_date), '')::date AS order_date,
    NULLIF(BTRIM(due_date), '')::date AS due_date,
    NULLIF(BTRIM(ship_date), '')::date AS ship_date,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.fact_internet_sales;

CREATE OR REPLACE VIEW staging.fact_reseller_sales AS
SELECT
    'Reseller'::text AS channel,
    CONCAT('R|', sales_order_number, '|', sales_order_line_number) AS sales_line_id,
    NULLIF(BTRIM(product_key), '')::integer AS product_key,
    NULLIF(BTRIM(order_date_key), '')::integer AS order_date_key,
    NULLIF(BTRIM(due_date_key), '')::integer AS due_date_key,
    NULLIF(BTRIM(ship_date_key), '')::integer AS ship_date_key,
    NULL::integer AS customer_key,
    NULLIF(BTRIM(reseller_key), '')::integer AS reseller_key,
    NULLIF(BTRIM(employee_key), '')::integer AS employee_key,
    NULLIF(BTRIM(promotion_key), '')::integer AS promotion_key,
    NULLIF(BTRIM(currency_key), '')::integer AS currency_key,
    NULLIF(BTRIM(sales_territory_key), '')::integer AS sales_territory_key,
    NULLIF(BTRIM(sales_order_number), '') AS sales_order_number,
    NULLIF(BTRIM(sales_order_line_number), '')::smallint AS sales_order_line_number,
    NULLIF(BTRIM(revision_number), '')::smallint AS revision_number,
    NULLIF(BTRIM(order_quantity), '')::integer AS order_quantity,
    NULLIF(BTRIM(unit_price), '')::numeric(19,4) AS unit_price,
    NULLIF(BTRIM(extended_amount), '')::numeric(19,4) AS extended_amount,
    NULLIF(BTRIM(unit_price_discount_pct), '')::numeric(12,6) AS unit_price_discount_pct,
    NULLIF(BTRIM(discount_amount), '')::numeric(19,4) AS discount_amount,
    NULLIF(BTRIM(product_standard_cost), '')::numeric(19,4) AS product_standard_cost,
    NULLIF(BTRIM(total_product_cost), '')::numeric(19,4) AS total_product_cost,
    NULLIF(BTRIM(sales_amount), '')::numeric(19,4) AS sales_amount,
    NULLIF(BTRIM(tax_amt), '')::numeric(19,4) AS tax_amount,
    NULLIF(BTRIM(freight), '')::numeric(19,4) AS freight,
    (
        NULLIF(BTRIM(sales_amount), '')::numeric(19,4)
        - NULLIF(BTRIM(total_product_cost), '')::numeric(19,4)
    ) AS gross_profit,
    (
        NULLIF(BTRIM(sales_amount), '')::numeric
        - NULLIF(BTRIM(total_product_cost), '')::numeric
    ) / NULLIF(NULLIF(BTRIM(sales_amount), '')::numeric, 0) AS gross_margin_pct,
    NULLIF(BTRIM(order_date), '')::date AS order_date,
    NULLIF(BTRIM(due_date), '')::date AS due_date,
    NULLIF(BTRIM(ship_date), '')::date AS ship_date,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.fact_reseller_sales;

CREATE OR REPLACE VIEW staging.fact_sales AS
SELECT * FROM staging.fact_internet_sales
UNION ALL
SELECT * FROM staging.fact_reseller_sales;

CREATE OR REPLACE VIEW staging.fact_product_inventory AS
SELECT
    NULLIF(BTRIM(product_key), '')::integer AS product_key,
    NULLIF(BTRIM(date_key), '')::integer AS date_key,
    NULLIF(BTRIM(movement_date), '')::date AS movement_date,
    NULLIF(BTRIM(unit_cost), '')::numeric(19,4) AS unit_cost,
    NULLIF(BTRIM(units_in), '')::integer AS units_in,
    NULLIF(BTRIM(units_out), '')::integer AS units_out,
    NULLIF(BTRIM(units_balance), '')::integer AS units_balance,
    (
        NULLIF(BTRIM(units_in), '')::integer
        - NULLIF(BTRIM(units_out), '')::integer
    ) AS net_units_movement,
    (
        NULLIF(BTRIM(unit_cost), '')::numeric(19,4)
        * NULLIF(BTRIM(units_balance), '')::integer
    ) AS inventory_value,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.fact_product_inventory;
