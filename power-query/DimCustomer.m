let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT customer_key, customer_code, customer_name, title, first_name, middle_name, last_name, birth_date, marital_status, gender, email_address, yearly_income, total_children, children_at_home, education, occupation, is_house_owner, cars_owned, first_purchase_date, commute_distance FROM analytics.dim_customer"
        ]
    )
in
    Source
