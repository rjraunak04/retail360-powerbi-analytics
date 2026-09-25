"""Read-only PostgreSQL analytics tool for Retail360."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import psycopg
from psycopg import sql

from ..config import AgentConfig
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
    """Return normalized SQL when it is safe for the analytics tool."""

    normalized = query.strip()
    if not normalized:
        raise QueryRejected("Query must not be empty.")

    # One statement only. A single optional trailing semicolon is accepted.
    body = normalized[:-1].strip() if normalized.endswith(";") else normalized
    if ";" in body:
        raise QueryRejected("Only one SQL statement is allowed.")

    if not re.match(r"^(select|with)\b", body, re.IGNORECASE):
        raise QueryRejected("Only SELECT or WITH queries are allowed.")

    if _FORBIDDEN.search(body):
        raise QueryRejected("Mutating or administrative SQL is not allowed.")

    schemas = {match.group(2).lower() for match in _SCHEMA_REF.finditer(body)}
    disallowed = schemas - {allowed_schema.lower()}
    if disallowed:
        raise QueryRejected(
            "Query references a non-approved schema: " + ", ".join(sorted(disallowed))
        )

    return body


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
            safe_query = validate_read_only_query(query, self.config.allowed_schema)
        except QueryRejected as exc:
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
                error=f"PostgreSQL query failed: {exc}",
                metadata={"rejected": False},
            )
