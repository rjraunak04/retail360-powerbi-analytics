let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT geography_key, city, state_province_code, state_province_name, country_region_code, country_name, postal_code, territory_region, territory_country, territory_group FROM analytics.dim_geography"
        ]
    )
in
    Source
