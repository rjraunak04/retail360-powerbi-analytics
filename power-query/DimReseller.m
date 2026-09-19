let
    Source = PostgreSQL.Database(pServer, pDatabase, [CreateNavigationProperties=false]),
    Analytics = Source{[Schema="analytics", Item="dim_reseller"]}[Data]
in
    Analytics
