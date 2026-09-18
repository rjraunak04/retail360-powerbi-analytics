-- Retail360 Stage 3: typed business dimensions
-- Raw tables remain source-aligned; staging exposes typed, business-friendly views.

CREATE OR REPLACE VIEW staging.dim_date AS
SELECT
    NULLIF(BTRIM(date_key), '')::integer AS date_key,
    NULLIF(BTRIM(full_date_alternate_key), '')::date AS date,
    NULLIF(BTRIM(day_number_of_week), '')::smallint AS day_of_week,
    english_day_name_of_week AS day_name,
    NULLIF(BTRIM(day_number_of_month), '')::smallint AS day_of_month,
    NULLIF(BTRIM(day_number_of_year), '')::smallint AS day_of_year,
    NULLIF(BTRIM(week_number_of_year), '')::smallint AS week_of_year,
    english_month_name AS month_name,
    NULLIF(BTRIM(month_number_of_year), '')::smallint AS month_number,
    NULLIF(BTRIM(calendar_quarter), '')::smallint AS calendar_quarter,
    NULLIF(BTRIM(calendar_year), '')::integer AS calendar_year,
    NULLIF(BTRIM(calendar_semester), '')::smallint AS calendar_semester,
    NULLIF(BTRIM(fiscal_quarter), '')::smallint AS fiscal_quarter,
    NULLIF(BTRIM(fiscal_year), '')::integer AS fiscal_year,
    NULLIF(BTRIM(fiscal_semester), '')::smallint AS fiscal_semester,
    (
        NULLIF(BTRIM(calendar_year), '')::integer * 100
        + NULLIF(BTRIM(month_number_of_year), '')::integer
    ) AS year_month_key,
    TO_CHAR(NULLIF(BTRIM(full_date_alternate_key), '')::date, 'YYYY-MM') AS year_month,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_date;

CREATE OR REPLACE VIEW staging.dim_currency AS
SELECT
    NULLIF(BTRIM(currency_key), '')::integer AS currency_key,
    NULLIF(BTRIM(currency_alternate_key), '') AS currency_code,
    NULLIF(BTRIM(currency_name), '') AS currency_name,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_currency;

CREATE OR REPLACE VIEW staging.dim_sales_territory AS
SELECT
    NULLIF(BTRIM(sales_territory_key), '')::integer AS sales_territory_key,
    NULLIF(BTRIM(sales_territory_alternate_key), '')::integer AS sales_territory_alternate_key,
    NULLIF(BTRIM(sales_territory_region), '') AS territory_region,
    NULLIF(BTRIM(sales_territory_country), '') AS territory_country,
    NULLIF(BTRIM(sales_territory_group), '') AS territory_group,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_sales_territory;

CREATE OR REPLACE VIEW staging.dim_geography AS
SELECT
    NULLIF(BTRIM(g.geography_key), '')::integer AS geography_key,
    NULLIF(BTRIM(g.city), '') AS city,
    NULLIF(BTRIM(g.state_province_code), '') AS state_province_code,
    NULLIF(BTRIM(g.state_province_name), '') AS state_province_name,
    NULLIF(BTRIM(g.country_region_code), '') AS country_region_code,
    NULLIF(BTRIM(g.english_country_region_name), '') AS country_name,
    NULLIF(BTRIM(g.postal_code), '') AS postal_code,
    NULLIF(BTRIM(g.sales_territory_key), '')::integer AS sales_territory_key,
    NULLIF(BTRIM(t.sales_territory_region), '') AS territory_region,
    NULLIF(BTRIM(t.sales_territory_country), '') AS territory_country,
    NULLIF(BTRIM(t.sales_territory_group), '') AS territory_group,
    g._source_file,
    g._source_row_number,
    g._loaded_at
FROM raw.dim_geography g
LEFT JOIN raw.dim_sales_territory t
    ON NULLIF(BTRIM(g.sales_territory_key), '')::integer
     = NULLIF(BTRIM(t.sales_territory_key), '')::integer;

CREATE OR REPLACE VIEW staging.dim_product AS
SELECT
    NULLIF(BTRIM(p.product_key), '')::integer AS product_key,
    NULLIF(BTRIM(p.product_alternate_key), '') AS product_code,
    NULLIF(BTRIM(p.product_subcategory_key), '')::integer AS product_subcategory_key,
    NULLIF(BTRIM(s.product_category_key), '')::integer AS product_category_key,
    NULLIF(BTRIM(p.english_product_name), '') AS product_name,
    NULLIF(BTRIM(s.english_product_subcategory_name), '') AS subcategory_name,
    NULLIF(BTRIM(c.english_product_category_name), '') AS category_name,
    NULLIF(BTRIM(p.standard_cost), '')::numeric(19,4) AS standard_cost,
    NULLIF(BTRIM(p.list_price), '')::numeric(19,4) AS list_price,
    NULLIF(BTRIM(p.dealer_price), '')::numeric(19,4) AS dealer_price,
    NULLIF(BTRIM(p.color), '') AS color,
    NULLIF(BTRIM(p.size), '') AS size,
    NULLIF(BTRIM(p.size_range), '') AS size_range,
    NULLIF(BTRIM(p.weight), '')::numeric(18,4) AS weight,
    NULLIF(BTRIM(p.safety_stock_level), '')::integer AS safety_stock_level,
    NULLIF(BTRIM(p.reorder_point), '')::integer AS reorder_point,
    NULLIF(BTRIM(p.days_to_manufacture), '')::integer AS days_to_manufacture,
    NULLIF(BTRIM(p.product_line), '') AS product_line,
    NULLIF(BTRIM(p.class), '') AS product_class,
    NULLIF(BTRIM(p.style), '') AS style,
    NULLIF(BTRIM(p.model_name), '') AS model_name,
    NULLIF(BTRIM(p.start_date), '')::date AS start_date,
    NULLIF(BTRIM(p.end_date), '')::date AS end_date,
    NULLIF(BTRIM(p.status), '') AS status,
    p._source_file,
    p._source_row_number,
    p._loaded_at
FROM raw.dim_product p
LEFT JOIN raw.dim_product_subcategory s
    ON NULLIF(BTRIM(p.product_subcategory_key), '')::integer
     = NULLIF(BTRIM(s.product_subcategory_key), '')::integer
LEFT JOIN raw.dim_product_category c
    ON NULLIF(BTRIM(s.product_category_key), '')::integer
     = NULLIF(BTRIM(c.product_category_key), '')::integer;

CREATE OR REPLACE VIEW staging.dim_customer AS
SELECT
    NULLIF(BTRIM(customer_key), '')::integer AS customer_key,
    NULLIF(BTRIM(geography_key), '')::integer AS geography_key,
    NULLIF(BTRIM(customer_alternate_key), '') AS customer_code,
    NULLIF(BTRIM(title), '') AS title,
    NULLIF(BTRIM(first_name), '') AS first_name,
    NULLIF(BTRIM(middle_name), '') AS middle_name,
    NULLIF(BTRIM(last_name), '') AS last_name,
    CONCAT_WS(' ',
        NULLIF(BTRIM(first_name), ''),
        NULLIF(BTRIM(middle_name), ''),
        NULLIF(BTRIM(last_name), '')
    ) AS customer_name,
    NULLIF(BTRIM(birth_date), '')::date AS birth_date,
    NULLIF(BTRIM(marital_status), '') AS marital_status,
    NULLIF(BTRIM(gender), '') AS gender,
    NULLIF(BTRIM(email_address), '') AS email_address,
    NULLIF(BTRIM(yearly_income), '')::numeric(19,2) AS yearly_income,
    NULLIF(BTRIM(total_children), '')::integer AS total_children,
    NULLIF(BTRIM(number_children_at_home), '')::integer AS children_at_home,
    NULLIF(BTRIM(english_education), '') AS education,
    NULLIF(BTRIM(english_occupation), '') AS occupation,
    CASE
        WHEN BTRIM(house_owner_flag) = '1' THEN true
        WHEN BTRIM(house_owner_flag) = '0' THEN false
        ELSE NULL
    END AS is_house_owner,
    NULLIF(BTRIM(number_cars_owned), '')::integer AS cars_owned,
    NULLIF(BTRIM(date_first_purchase), '')::date AS first_purchase_date,
    NULLIF(BTRIM(commute_distance), '') AS commute_distance,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_customer;

CREATE OR REPLACE VIEW staging.dim_reseller AS
SELECT
    NULLIF(BTRIM(reseller_key), '')::integer AS reseller_key,
    NULLIF(BTRIM(geography_key), '')::integer AS geography_key,
    NULLIF(BTRIM(reseller_alternate_key), '') AS reseller_code,
    NULLIF(BTRIM(reseller_name), '') AS reseller_name,
    NULLIF(BTRIM(business_type), '') AS business_type,
    NULLIF(BTRIM(number_employees), '')::integer AS number_employees,
    NULLIF(BTRIM(order_frequency), '') AS order_frequency,
    NULLIF(BTRIM(order_month), '')::smallint AS order_month,
    NULLIF(BTRIM(first_order_year), '')::integer AS first_order_year,
    NULLIF(BTRIM(last_order_year), '')::integer AS last_order_year,
    NULLIF(BTRIM(product_line), '') AS product_line,
    NULLIF(BTRIM(annual_sales), '')::numeric(19,2) AS annual_sales,
    NULLIF(BTRIM(annual_revenue), '')::numeric(19,2) AS annual_revenue,
    NULLIF(BTRIM(year_opened), '')::integer AS year_opened,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_reseller;

CREATE OR REPLACE VIEW staging.dim_promotion AS
SELECT
    NULLIF(BTRIM(promotion_key), '')::integer AS promotion_key,
    NULLIF(BTRIM(promotion_alternate_key), '')::integer AS promotion_alternate_key,
    NULLIF(BTRIM(english_promotion_name), '') AS promotion_name,
    NULLIF(BTRIM(discount_pct), '')::numeric(12,6) AS discount_pct,
    NULLIF(BTRIM(english_promotion_type), '') AS promotion_type,
    NULLIF(BTRIM(english_promotion_category), '') AS promotion_category,
    NULLIF(BTRIM(start_date), '')::date AS start_date,
    NULLIF(BTRIM(end_date), '')::date AS end_date,
    NULLIF(BTRIM(min_qty), '')::integer AS min_qty,
    NULLIF(BTRIM(max_qty), '')::integer AS max_qty,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_promotion;

CREATE OR REPLACE VIEW staging.dim_employee AS
SELECT
    NULLIF(BTRIM(employee_key), '')::integer AS employee_key,
    NULLIF(BTRIM(parent_employee_key), '')::integer AS parent_employee_key,
    NULLIF(BTRIM(sales_territory_key), '')::integer AS sales_territory_key,
    CONCAT_WS(' ',
        NULLIF(BTRIM(first_name), ''),
        NULLIF(BTRIM(middle_name), ''),
        NULLIF(BTRIM(last_name), '')
    ) AS employee_name,
    NULLIF(BTRIM(title), '') AS title,
    NULLIF(BTRIM(hire_date), '')::date AS hire_date,
    NULLIF(BTRIM(department_name), '') AS department_name,
    CASE
        WHEN BTRIM(current_flag) = '1' THEN true
        WHEN BTRIM(current_flag) = '0' THEN false
        ELSE NULL
    END AS is_current,
    CASE
        WHEN BTRIM(sales_person_flag) = '1' THEN true
        WHEN BTRIM(sales_person_flag) = '0' THEN false
        ELSE NULL
    END AS is_sales_person,
    NULLIF(BTRIM(start_date), '')::date AS start_date,
    NULLIF(BTRIM(end_date), '')::date AS end_date,
    NULLIF(BTRIM(status), '') AS status,
    _source_file,
    _source_row_number,
    _loaded_at
FROM raw.dim_employee;
