let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT product_key, date_key, movement_date, unit_cost, units_in, units_out, units_balance, net_units_movement, inventory_value FROM analytics.fact_inventory"
        ]
    )
in
    Source
