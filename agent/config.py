"""Configuration for the Retail360 analytics agent."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    """Safety-first defaults for agent tool execution."""

    max_rows: int = 100
    statement_timeout_seconds: int = 15
    allowed_schema: str = "analytics"
    require_read_only: bool = True
