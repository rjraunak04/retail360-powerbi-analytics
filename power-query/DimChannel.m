let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT channel_key, channel_name FROM analytics.dim_channel"
        ]
    )
in
    Source
