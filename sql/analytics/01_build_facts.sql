-- Retail360 Stage 4: analytics star-schema facts

CREATE TABLE analytics.fact_sales (
    sales_line_id text PRIMARY KEY,
    channel_key smallint NOT NULL,
    product_key integer NOT NULL,
    order_date_key integer NOT NULL,
    due_date_key integer NOT NULL,
    ship_date_key integer NOT NULL,
    customer_key integer NOT NULL,
    reseller_key integer NOT NULL,
    employee_key integer NOT NULL,
    promotion_key integer NOT NULL,
    currency_key integer NOT NULL,
    sales_territory_key integer NOT NULL,
    geography_key integer NOT NULL,
    sales_order_number text NOT NULL,
    sales_order_line_number smallint NOT NULL,
    revision_number smallint,
    order_quantity integer NOT NULL,
    unit_price numeric(19,4) NOT NULL,
    extended_amount numeric(19,4) NOT NULL,
    unit_price_discount_pct numeric(12,6) NOT NULL,
    discount_amount numeric(19,4) NOT NULL,
    product_standard_cost numeric(19,4) NOT NULL,
    total_product_cost numeric(19,4) NOT NULL,
    sales_amount numeric(19,4) NOT NULL,
    tax_amount numeric(19,4) NOT NULL,
    freight numeric(19,4) NOT NULL,
    gross_profit numeric(19,4) NOT NULL,
    gross_margin_pct numeric,
    order_date date NOT NULL,
    due_date date NOT NULL,
    ship_date date NOT NULL
);

INSERT INTO analytics.fact_sales
SELECT
    f.sales_line_id,
    CASE f.channel WHEN 'Internet' THEN 1 WHEN 'Reseller' THEN 2 ELSE 0 END::smallint,
    COALESCE(f.product_key, 0),
    COALESCE(f.order_date_key, 0),
    COALESCE(f.due_date_key, 0),
    COALESCE(f.ship_date_key, 0),
    COALESCE(f.customer_key, 0),
    COALESCE(f.reseller_key, 0),
    COALESCE(f.employee_key, 0),
    COALESCE(f.promotion_key, 0),
    COALESCE(f.currency_key, 0),
    COALESCE(f.sales_territory_key, 0),
    COALESCE(
        CASE
            WHEN f.channel = 'Internet' THEN c.geography_key
            WHEN f.channel = 'Reseller' THEN r.geography_key
        END,
        0
    ) AS geography_key,
    f.sales_order_number,
    f.sales_order_line_number,
    f.revision_number,
    f.order_quantity,
    f.unit_price,
    f.extended_amount,
    f.unit_price_discount_pct,
    f.discount_amount,
    f.product_standard_cost,
    f.total_product_cost,
    f.sales_amount,
    f.tax_amount,
    f.freight,
    f.gross_profit,
    f.gross_margin_pct,
    f.order_date,
    f.due_date,
    f.ship_date
FROM staging.fact_sales f
LEFT JOIN staging.dim_customer c
    ON f.customer_key = c.customer_key
LEFT JOIN staging.dim_reseller r
    ON f.reseller_key = r.reseller_key;

CREATE TABLE analytics.fact_inventory (
    product_key integer NOT NULL,
    date_key integer NOT NULL,
    movement_date date NOT NULL,
    unit_cost numeric(19,4) NOT NULL,
    units_in integer NOT NULL,
    units_out integer NOT NULL,
    units_balance integer NOT NULL,
    net_units_movement integer NOT NULL,
    inventory_value numeric(23,4) NOT NULL,
    PRIMARY KEY (product_key, date_key)
);

INSERT INTO analytics.fact_inventory
SELECT
    COALESCE(product_key, 0),
    COALESCE(date_key, 0),
    movement_date,
    unit_cost,
    units_in,
    units_out,
    units_balance,
    net_units_movement,
    inventory_value
FROM staging.fact_product_inventory;
