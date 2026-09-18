-- Retail360 Stage 2: raw landing tables
-- All source attributes are intentionally TEXT in the raw layer.
-- Typing, standardisation, constraints, and business rules belong in staging/analytics.

DROP TABLE IF EXISTS raw.dim_currency CASCADE;
CREATE TABLE raw.dim_currency (
    currency_key text,
    currency_alternate_key text,
    currency_name text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_customer CASCADE;
CREATE TABLE raw.dim_customer (
    customer_key text,
    geography_key text,
    customer_alternate_key text,
    title text,
    first_name text,
    middle_name text,
    last_name text,
    name_style text,
    birth_date text,
    marital_status text,
    suffix text,
    gender text,
    email_address text,
    yearly_income text,
    total_children text,
    number_children_at_home text,
    english_education text,
    spanish_education text,
    french_education text,
    english_occupation text,
    spanish_occupation text,
    french_occupation text,
    house_owner_flag text,
    number_cars_owned text,
    address_line1 text,
    address_line2 text,
    phone text,
    date_first_purchase text,
    commute_distance text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_date CASCADE;
CREATE TABLE raw.dim_date (
    date_key text,
    full_date_alternate_key text,
    day_number_of_week text,
    english_day_name_of_week text,
    spanish_day_name_of_week text,
    french_day_name_of_week text,
    day_number_of_month text,
    day_number_of_year text,
    week_number_of_year text,
    english_month_name text,
    spanish_month_name text,
    french_month_name text,
    month_number_of_year text,
    calendar_quarter text,
    calendar_year text,
    calendar_semester text,
    fiscal_quarter text,
    fiscal_year text,
    fiscal_semester text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_employee CASCADE;
CREATE TABLE raw.dim_employee (
    employee_key text,
    parent_employee_key text,
    employee_national_id_alternate_key text,
    parent_employee_national_id_alternate_key text,
    sales_territory_key text,
    first_name text,
    last_name text,
    middle_name text,
    name_style text,
    title text,
    hire_date text,
    birth_date text,
    login_id text,
    email_address text,
    phone text,
    marital_status text,
    emergency_contact_name text,
    emergency_contact_phone text,
    salaried_flag text,
    gender text,
    pay_frequency text,
    base_rate text,
    vacation_hours text,
    sick_leave_hours text,
    current_flag text,
    sales_person_flag text,
    department_name text,
    start_date text,
    end_date text,
    status text,
    employee_photo text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_geography CASCADE;
CREATE TABLE raw.dim_geography (
    geography_key text,
    city text,
    state_province_code text,
    state_province_name text,
    country_region_code text,
    english_country_region_name text,
    spanish_country_region_name text,
    french_country_region_name text,
    postal_code text,
    sales_territory_key text,
    ip_address_locator text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_product CASCADE;
CREATE TABLE raw.dim_product (
    product_key text,
    product_alternate_key text,
    product_subcategory_key text,
    weight_unit_measure_code text,
    size_unit_measure_code text,
    english_product_name text,
    spanish_product_name text,
    french_product_name text,
    standard_cost text,
    finished_goods_flag text,
    color text,
    safety_stock_level text,
    reorder_point text,
    list_price text,
    size text,
    size_range text,
    weight text,
    days_to_manufacture text,
    product_line text,
    dealer_price text,
    class text,
    style text,
    model_name text,
    large_photo text,
    english_description text,
    french_description text,
    chinese_description text,
    arabic_description text,
    hebrew_description text,
    thai_description text,
    german_description text,
    japanese_description text,
    turkish_description text,
    start_date text,
    end_date text,
    status text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_product_category CASCADE;
CREATE TABLE raw.dim_product_category (
    product_category_key text,
    product_category_alternate_key text,
    english_product_category_name text,
    spanish_product_category_name text,
    french_product_category_name text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_product_subcategory CASCADE;
CREATE TABLE raw.dim_product_subcategory (
    product_subcategory_key text,
    product_subcategory_alternate_key text,
    english_product_subcategory_name text,
    spanish_product_subcategory_name text,
    french_product_subcategory_name text,
    product_category_key text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_promotion CASCADE;
CREATE TABLE raw.dim_promotion (
    promotion_key text,
    promotion_alternate_key text,
    english_promotion_name text,
    spanish_promotion_name text,
    french_promotion_name text,
    discount_pct text,
    english_promotion_type text,
    spanish_promotion_type text,
    french_promotion_type text,
    english_promotion_category text,
    spanish_promotion_category text,
    french_promotion_category text,
    start_date text,
    end_date text,
    min_qty text,
    max_qty text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_reseller CASCADE;
CREATE TABLE raw.dim_reseller (
    reseller_key text,
    geography_key text,
    reseller_alternate_key text,
    phone text,
    business_type text,
    reseller_name text,
    number_employees text,
    order_frequency text,
    order_month text,
    first_order_year text,
    last_order_year text,
    product_line text,
    address_line1 text,
    address_line2 text,
    annual_sales text,
    bank_name text,
    min_payment_type text,
    min_payment_amount text,
    annual_revenue text,
    year_opened text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.dim_sales_territory CASCADE;
CREATE TABLE raw.dim_sales_territory (
    sales_territory_key text,
    sales_territory_alternate_key text,
    sales_territory_region text,
    sales_territory_country text,
    sales_territory_group text,
    sales_territory_image text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.fact_internet_sales CASCADE;
CREATE TABLE raw.fact_internet_sales (
    product_key text,
    order_date_key text,
    due_date_key text,
    ship_date_key text,
    customer_key text,
    promotion_key text,
    currency_key text,
    sales_territory_key text,
    sales_order_number text,
    sales_order_line_number text,
    revision_number text,
    order_quantity text,
    unit_price text,
    extended_amount text,
    unit_price_discount_pct text,
    discount_amount text,
    product_standard_cost text,
    total_product_cost text,
    sales_amount text,
    tax_amt text,
    freight text,
    carrier_tracking_number text,
    customer_po_number text,
    order_date text,
    due_date text,
    ship_date text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.fact_reseller_sales CASCADE;
CREATE TABLE raw.fact_reseller_sales (
    product_key text,
    order_date_key text,
    due_date_key text,
    ship_date_key text,
    reseller_key text,
    employee_key text,
    promotion_key text,
    currency_key text,
    sales_territory_key text,
    sales_order_number text,
    sales_order_line_number text,
    revision_number text,
    order_quantity text,
    unit_price text,
    extended_amount text,
    unit_price_discount_pct text,
    discount_amount text,
    product_standard_cost text,
    total_product_cost text,
    sales_amount text,
    tax_amt text,
    freight text,
    carrier_tracking_number text,
    customer_po_number text,
    order_date text,
    due_date text,
    ship_date text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS raw.fact_product_inventory CASCADE;
CREATE TABLE raw.fact_product_inventory (
    product_key text,
    date_key text,
    movement_date text,
    unit_cost text,
    units_in text,
    units_out text,
    units_balance text,
    _source_file text NOT NULL,
    _source_row_number bigint NOT NULL,
    _loaded_at timestamptz NOT NULL DEFAULT now()
);

