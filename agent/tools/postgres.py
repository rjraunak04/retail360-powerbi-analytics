"""Read-only PostgreSQL analytics tool for Retail360."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import psycopg
from psycopg import sql

from ..config import AgentConfig
from ..guardrails import GuardrailViolation, SqlGuardrailPolicy, validate_agent_sql
from .base import ToolResult

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|merge|drop|alter|truncate|create|grant|revoke|"
    r"copy|call|do|vacuum|analyze|refresh|reindex|cluster|comment|set|reset|"
    r"listen|notify|prepare|execute|deallocate)\b",
    re.IGNORECASE,
)
_SCHEMA_REF = re.compile(
    r'(?<![\w"])("?)([A-Za-z_][\w$]*)\1\s*\.',
    re.IGNORECASE,
)


class QueryRejected(ValueError):
    """Raised when a query violates the Retail360 read-only contract."""


def validate_read_only_query(query: str, allowed_schema: str = "analytics") -> str:
    """Compatibility wrapper around the stronger Day 5 guardrail layer."""

    try:
        return validate_agent_sql(query, SqlGuardrailPolicy(allowed_schema=allowed_schema))
    except GuardrailViolation as exc:
        raise QueryRejected(str(exc)) from exc


class PostgresAnalyticsTool:
    """Execute bounded, read-only SQL against Retail360's analytics schema."""

    name = "postgres_analytics"
    description = (
        "Run a read-only SELECT query against the governed Retail360 analytics schema."
    )

    def __init__(
        self,
        config: AgentConfig | None = None,
        connection_factory: Callable[..., Any] = psycopg.connect,
    ) -> None:
        self.config = config or AgentConfig()
        self._connect = connection_factory

    def run(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query")
        if not isinstance(query, str):
            return ToolResult(
                tool_name=self.name,
                ok=False,
                error="query must be a SQL string",
            )

        try:
            safe_query = validate_agent_sql(
                query,
                SqlGuardrailPolicy(
                    allowed_schema=self.config.allowed_schema,
                    allowed_tables=frozenset(self.config.allowed_tables),
                    max_query_chars=self.config.max_query_chars,
                ),
            )
        except (QueryRejected, GuardrailViolation) as exc:
            return ToolResult(
                tool_name=self.name,
                ok=False,
                error=str(exc),
                metadata={"rejected": True},
            )

        try:
            with self._connect() as connection:
                connection.read_only = True
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql.SQL("SET LOCAL statement_timeout = {}").format(
                            sql.Literal(self.config.statement_timeout_seconds * 1000)
                        )
                    )
                    cursor.execute(safe_query)
                    columns = tuple(
                        item.name if hasattr(item, "name") else item[0]
                        for item in (cursor.description or ())
                    )
                    rows = cursor.fetchmany(self.config.max_rows + 1)

            truncated = len(rows) > self.config.max_rows
            rows = rows[: self.config.max_rows]
            data = [dict(zip(columns, row)) for row in rows]
            return ToolResult(
                tool_name=self.name,
                ok=True,
                data=data,
                metadata={
                    "row_count": len(data),
                    "truncated": truncated,
                    "max_rows": self.config.max_rows,
                    "read_only": True,
                    "allowed_schema": self.config.allowed_schema,
                },
            )
        except Exception as exc:  # Boundary: normalize DB failures for the agent.
            return ToolResult(
                tool_name=self.name,
                ok=False,
                error="PostgreSQL query failed safely.",
                metadata={"rejected": False},
            )
