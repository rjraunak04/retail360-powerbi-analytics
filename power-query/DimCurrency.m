let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT currency_key, currency_code, currency_name FROM analytics.dim_currency"
        ]
    )
in
    Source
