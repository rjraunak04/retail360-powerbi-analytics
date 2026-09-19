let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT promotion_key, promotion_alternate_key, promotion_name, discount_pct, promotion_type, promotion_category, start_date, end_date, min_qty, max_qty FROM analytics.dim_promotion"
        ]
    )
in
    Source
