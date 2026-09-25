"""Shared contracts for deterministic agent tools."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class ToolResult:
    """Normalized result returned by every agent tool."""

    tool_name: str
    ok: bool
    data: Any = None
    error: str | None = None
    metadata: Mapping[str, Any] | None = None


class AgentTool(Protocol):
    """Minimal contract implemented by every Retail360 agent tool."""

    name: str
    description: str

    def run(self, **kwargs: Any) -> ToolResult:
        """Execute a deterministic tool operation."""
        ...
