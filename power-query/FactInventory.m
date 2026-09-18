let
    Source = PostgreSQL.Database(pServer, pDatabase, [CreateNavigationProperties=false]),
    Analytics = Source{[Schema="analytics", Item="fact_inventory"]}[Data]
in
    Analytics
