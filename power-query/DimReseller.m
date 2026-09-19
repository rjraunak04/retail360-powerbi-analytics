let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT reseller_key, reseller_code, reseller_name, business_type, number_employees, order_frequency, order_month, first_order_year, last_order_year, product_line, annual_sales, annual_revenue, year_opened FROM analytics.dim_reseller"
        ]
    )
in
    Source
