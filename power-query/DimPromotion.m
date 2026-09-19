let
    Source = PostgreSQL.Database(pServer, pDatabase, [CreateNavigationProperties=false]),
    Analytics = Source{[Schema="analytics", Item="dim_promotion"]}[Data]
in
    Analytics
