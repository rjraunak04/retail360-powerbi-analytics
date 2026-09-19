let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT sales_territory_key, sales_territory_alternate_key, territory_region, territory_country, territory_group FROM analytics.dim_sales_territory"
        ]
    )
in
    Source
