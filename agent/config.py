"""Configuration for the Retail360 analytics agent."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    """Safety-first defaults for agent tool execution."""

    max_rows: int = 100
    statement_timeout_seconds: int = 15
    allowed_schema: str = "analytics"
    require_read_only: bool = True
    max_query_chars: int = 12000
    allowed_tables: tuple[str, ...] = (
        "dim_date",
        "dim_product",
        "dim_customer",
        "dim_reseller",
        "dim_employee",
        "dim_geography",
        "dim_sales_territory",
        "dim_promotion",
        "dim_currency",
        "dim_channel",
        "fact_sales",
        "fact_inventory",
    )
