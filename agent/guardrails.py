"""Deterministic guardrails for agent-generated analytical SQL."""

from __future__ import annotations

import re
from dataclasses import dataclass

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(insert|update|delete|merge|drop|alter|truncate|create|grant|revoke|"
    r"copy|call|do|vacuum|analyze|refresh|reindex|cluster|comment|set|reset|"
    r"listen|notify|prepare|execute|deallocate|lock|discard)\b",
    re.IGNORECASE,
)
_SCHEMA_REFERENCE = re.compile(r'(?<![\w"])("?)([A-Za-z_][\w$]*)\1\s*\.', re.IGNORECASE)
_TABLE_REFERENCE = re.compile(
    r"\b(?:from|join)\s+(?:analytics\.)?([A-Za-z_][\w$]*)",
    re.IGNORECASE,
)
_DANGEROUS_FUNCTION = re.compile(
    r"\b(pg_read_file|pg_read_binary_file|pg_ls_dir|pg_stat_file|"
    r"pg_sleep|dblink|lo_import|lo_export)\s*\(",
    re.IGNORECASE,
)
_SQL_COMMENT = re.compile(r"(--|/\*|\*/)")
_QUOTED_STRING = re.compile(r"'(?:''|[^'])*'")


class GuardrailViolation(ValueError):
    """Raised when SQL violates an agent safety policy."""


@dataclass(frozen=True)
class SqlGuardrailPolicy:
    allowed_schema: str = "analytics"
    allowed_tables: frozenset[str] = frozenset()
    max_query_chars: int = 12000
    allow_comments: bool = False


def _without_string_literals(sql_text: str) -> str:
    return _QUOTED_STRING.sub("''", sql_text)


def validate_agent_sql(query: str, policy: SqlGuardrailPolicy) -> str:
    """Validate one bounded, read-only analytical statement."""

    normalized = query.strip()
    if not normalized:
        raise GuardrailViolation("Query must not be empty.")
    if len(normalized) > policy.max_query_chars:
        raise GuardrailViolation("Query exceeds the configured complexity boundary.")

    body = normalized[:-1].strip() if normalized.endswith(";") else normalized
    inspected = _without_string_literals(body)

    if ";" in inspected:
        raise GuardrailViolation("Only one SQL statement is allowed.")
    if not policy.allow_comments and _SQL_COMMENT.search(inspected):
        raise GuardrailViolation("SQL comments are not allowed in agent queries.")
    if not re.match(r"^(select|with)\b", inspected, re.IGNORECASE):
        raise GuardrailViolation("Only SELECT or WITH queries are allowed.")
    if _FORBIDDEN_KEYWORDS.search(inspected):
        raise GuardrailViolation("Mutating or administrative SQL is not allowed.")
    if _DANGEROUS_FUNCTION.search(inspected):
        raise GuardrailViolation("Unsafe PostgreSQL functions are not allowed.")

    schemas = {match.group(1).lower() for match in _QUALIFIED_REFERENCE.finditer(inspected)}
    disallowed_schemas = schemas - {policy.allowed_schema.lower()}
    if disallowed_schemas:
        raise GuardrailViolation("Query references a non-approved schema.")

    if policy.allowed_tables:
        tables = {match.group(1).lower() for match in _TABLE_REFERENCE.finditer(inspected)}
        cte_names = {match.group(1).lower() for match in _CTE_NAME.finditer(inspected)}
        disallowed_tables = tables - {name.lower() for name in policy.allowed_tables} - cte_names
        if disallowed_tables:
            raise GuardrailViolation("Query references a non-approved analytics table.")

    return body
