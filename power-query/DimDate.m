let
    Source = PostgreSQL.Database(
        pServer,
        pDatabase,
        [
            CreateNavigationProperties=false,
            Query="SELECT date_key, date, day_of_week, day_name, day_of_month, day_of_year, week_of_year, month_name, month_number, calendar_quarter, calendar_year, calendar_semester, fiscal_quarter, fiscal_year, fiscal_semester, year_month_key, year_month FROM analytics.dim_date"
        ]
    )
in
    Source
