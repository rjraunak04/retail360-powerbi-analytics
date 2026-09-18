-- Retail360 Stage 4: analytics star-schema dimensions
-- Physical tables are used for a stable Power BI-facing semantic source.

DROP TABLE IF EXISTS analytics.fact_inventory CASCADE;
DROP TABLE IF EXISTS analytics.fact_sales CASCADE;

DROP TABLE IF EXISTS analytics.dim_channel CASCADE;
DROP TABLE IF EXISTS analytics.dim_employee CASCADE;
DROP TABLE IF EXISTS analytics.dim_reseller CASCADE;
DROP TABLE IF EXISTS analytics.dim_customer CASCADE;
DROP TABLE IF EXISTS analytics.dim_geography CASCADE;
DROP TABLE IF EXISTS analytics.dim_sales_territory CASCADE;
DROP TABLE IF EXISTS analytics.dim_currency CASCADE;
DROP TABLE IF EXISTS analytics.dim_promotion CASCADE;
DROP TABLE IF EXISTS analytics.dim_product CASCADE;
DROP TABLE IF EXISTS analytics.dim_date CASCADE;

CREATE TABLE analytics.dim_date (
    date_key integer PRIMARY KEY,
    date date,
    day_of_week smallint,
    day_name text,
    day_of_month smallint,
    day_of_year smallint,
    week_of_year smallint,
    month_name text,
    month_number smallint,
    calendar_quarter smallint,
    calendar_year integer,
    calendar_semester smallint,
    fiscal_quarter smallint,
    fiscal_year integer,
    fiscal_semester smallint,
    year_month_key integer,
    year_month text
);

INSERT INTO analytics.dim_date
SELECT
    date_key, date, day_of_week, day_name, day_of_month, day_of_year,
    week_of_year, month_name, month_number, calendar_quarter, calendar_year,
    calendar_semester, fiscal_quarter, fiscal_year, fiscal_semester,
    year_month_key, year_month
FROM staging.dim_date;

INSERT INTO analytics.dim_date (date_key, day_name, month_name, year_month)
VALUES (0, 'Unknown', 'Unknown', 'Unknown')
ON CONFLICT (date_key) DO NOTHING;

CREATE UNIQUE INDEX ux_dim_date_date
    ON analytics.dim_date(date)
    WHERE date IS NOT NULL;

CREATE TABLE analytics.dim_product (
    product_key integer PRIMARY KEY,
    product_code text,
    product_name text NOT NULL,
    product_subcategory_key integer,
    subcategory_name text,
    product_category_key integer,
    category_name text,
    standard_cost numeric(19,4),
    list_price numeric(19,4),
    dealer_price numeric(19,4),
    color text,
    size text,
    size_range text,
    weight numeric(18,4),
    safety_stock_level integer,
    reorder_point integer,
    days_to_manufacture integer,
    product_line text,
    product_class text,
    style text,
    model_name text,
    start_date date,
    end_date date,
    status text
);

INSERT INTO analytics.dim_product
SELECT
    product_key, product_code, product_name, product_subcategory_key,
    subcategory_name, product_category_key, category_name, standard_cost,
    list_price, dealer_price, color, size, size_range, weight,
    safety_stock_level, reorder_point, days_to_manufacture, product_line,
    product_class, style, model_name, start_date, end_date, status
FROM staging.dim_product;

INSERT INTO analytics.dim_product (product_key, product_code, product_name, subcategory_name, category_name)
VALUES (0, 'UNKNOWN', 'Unknown / Not Applicable', 'Unknown', 'Unknown')
ON CONFLICT (product_key) DO NOTHING;

CREATE TABLE analytics.dim_customer (
    customer_key integer PRIMARY KEY,
    customer_code text,
    customer_name text NOT NULL,
    title text,
    first_name text,
    middle_name text,
    last_name text,
    birth_date date,
    marital_status text,
    gender text,
    email_address text,
    yearly_income numeric(19,2),
    total_children integer,
    children_at_home integer,
    education text,
    occupation text,
    is_house_owner boolean,
    cars_owned integer,
    first_purchase_date date,
    commute_distance text
);

INSERT INTO analytics.dim_customer
SELECT
    customer_key, customer_code, customer_name, title, first_name, middle_name,
    last_name, birth_date, marital_status, gender, email_address, yearly_income,
    total_children, children_at_home, education, occupation, is_house_owner,
    cars_owned, first_purchase_date, commute_distance
FROM staging.dim_customer;

INSERT INTO analytics.dim_customer (customer_key, customer_code, customer_name)
VALUES (0, 'N/A', 'Not Applicable / Unknown')
ON CONFLICT (customer_key) DO NOTHING;

CREATE TABLE analytics.dim_reseller (
    reseller_key integer PRIMARY KEY,
    reseller_code text,
    reseller_name text NOT NULL,
    business_type text,
    number_employees integer,
    order_frequency text,
    order_month smallint,
    first_order_year integer,
    last_order_year integer,
    product_line text,
    annual_sales numeric(19,2),
    annual_revenue numeric(19,2),
    year_opened integer
);

INSERT INTO analytics.dim_reseller
SELECT
    reseller_key, reseller_code, reseller_name, business_type, number_employees,
    order_frequency, order_month, first_order_year, last_order_year,
    product_line, annual_sales, annual_revenue, year_opened
FROM staging.dim_reseller;

INSERT INTO analytics.dim_reseller (reseller_key, reseller_code, reseller_name)
VALUES (0, 'N/A', 'Not Applicable / Unknown')
ON CONFLICT (reseller_key) DO NOTHING;

CREATE TABLE analytics.dim_employee (
    employee_key integer PRIMARY KEY,
    employee_name text NOT NULL,
    title text,
    hire_date date,
    department_name text,
    is_current boolean,
    is_sales_person boolean,
    start_date date,
    end_date date,
    status text
);

INSERT INTO analytics.dim_employee
SELECT
    employee_key, employee_name, title, hire_date, department_name,
    is_current, is_sales_person, start_date, end_date, status
FROM staging.dim_employee;

INSERT INTO analytics.dim_employee (employee_key, employee_name)
VALUES (0, 'Not Applicable / Unknown')
ON CONFLICT (employee_key) DO NOTHING;

CREATE TABLE analytics.dim_geography (
    geography_key integer PRIMARY KEY,
    city text,
    state_province_code text,
    state_province_name text,
    country_region_code text,
    country_name text,
    postal_code text,
    territory_region text,
    territory_country text,
    territory_group text
);

INSERT INTO analytics.dim_geography
SELECT
    geography_key, city, state_province_code, state_province_name,
    country_region_code, country_name, postal_code, territory_region,
    territory_country, territory_group
FROM staging.dim_geography;

INSERT INTO analytics.dim_geography (geography_key, city, state_province_name, country_name)
VALUES (0, 'Unknown', 'Unknown', 'Unknown')
ON CONFLICT (geography_key) DO NOTHING;

CREATE TABLE analytics.dim_sales_territory (
    sales_territory_key integer PRIMARY KEY,
    sales_territory_alternate_key integer,
    territory_region text,
    territory_country text,
    territory_group text
);

INSERT INTO analytics.dim_sales_territory
SELECT
    sales_territory_key, sales_territory_alternate_key,
    territory_region, territory_country, territory_group
FROM staging.dim_sales_territory;

INSERT INTO analytics.dim_sales_territory (
    sales_territory_key, territory_region, territory_country, territory_group
)
VALUES (0, 'Unknown', 'Unknown', 'Unknown')
ON CONFLICT (sales_territory_key) DO NOTHING;

CREATE TABLE analytics.dim_promotion (
    promotion_key integer PRIMARY KEY,
    promotion_alternate_key integer,
    promotion_name text NOT NULL,
    discount_pct numeric(12,6),
    promotion_type text,
    promotion_category text,
    start_date date,
    end_date date,
    min_qty integer,
    max_qty integer
);

INSERT INTO analytics.dim_promotion
SELECT
    promotion_key, promotion_alternate_key, promotion_name, discount_pct,
    promotion_type, promotion_category, start_date, end_date, min_qty, max_qty
FROM staging.dim_promotion;

INSERT INTO analytics.dim_promotion (promotion_key, promotion_name, promotion_type, promotion_category)
VALUES (0, 'Unknown / Not Applicable', 'Unknown', 'Unknown')
ON CONFLICT (promotion_key) DO NOTHING;

CREATE TABLE analytics.dim_currency (
    currency_key integer PRIMARY KEY,
    currency_code text,
    currency_name text NOT NULL
);

INSERT INTO analytics.dim_currency
SELECT currency_key, currency_code, currency_name
FROM staging.dim_currency;

INSERT INTO analytics.dim_currency (currency_key, currency_code, currency_name)
VALUES (0, 'UNK', 'Unknown')
ON CONFLICT (currency_key) DO NOTHING;

CREATE TABLE analytics.dim_channel (
    channel_key smallint PRIMARY KEY,
    channel_name text NOT NULL UNIQUE
);

INSERT INTO analytics.dim_channel (channel_key, channel_name)
VALUES
    (0, 'Unknown'),
    (1, 'Internet'),
    (2, 'Reseller');
