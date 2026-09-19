let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT sales_line_id, channel_key, product_key, order_date_key, due_date_key, ship_date_key, customer_key, reseller_key, employee_key, promotion_key, currency_key, sales_territory_key, geography_key, sales_order_number, sales_order_line_number, revision_number, order_quantity, unit_price, extended_amount, unit_price_discount_pct, discount_amount, product_standard_cost, total_product_cost, sales_amount, tax_amount, freight, gross_profit, gross_margin_pct, order_date, due_date, ship_date FROM analytics.fact_sales"
        ]
    )
in
    Source
