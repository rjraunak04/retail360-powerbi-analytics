let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT product_key, product_code, product_name, product_subcategory_key, subcategory_name, product_category_key, category_name, standard_cost, list_price, dealer_price, color, size, size_range, weight, safety_stock_level, reorder_point, days_to_manufacture, product_line, product_class, style, model_name, start_date, end_date, status FROM analytics.dim_product"
        ]
    )
in
    Source
