let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT employee_key, employee_name, title, hire_date, department_name, is_current, is_sales_person, start_date, end_date, status FROM analytics.dim_employee"
        ]
    )
in
    Source
