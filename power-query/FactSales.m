let
    Source = PostgreSQL.Database(pServer, pDatabase, [CreateNavigationProperties=false]),
    Analytics = Source{[Schema="analytics", Item="fact_sales"]}[Data]
in
    Analytics
