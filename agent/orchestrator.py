"""Small, provider-neutral orchestration layer for Retail360.

Day 1 intentionally contains no LLM dependency. The orchestrator establishes
the boundary between natural-language reasoning and deterministic tools first.
"""

from dataclasses import dataclass
from typing import Mapping

from .config import AgentConfig
from .tools import AgentTool, ToolResult


@dataclass(frozen=True)
class AgentResponse:
    """Structured response returned by the orchestrator."""

    question: str
    answer: str
    tool_results: tuple[ToolResult, ...] = ()


class AnalyticsAgent:
    """Registry-based orchestrator for governed Retail360 tools."""

    def __init__(
        self,
        tools: Mapping[str, AgentTool] | None = None,
        config: AgentConfig | None = None,
    ) -> None:
        self.config = config or AgentConfig()
        self._tools = dict(tools or {})

    @property
    def tool_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def register_tool(self, tool: AgentTool) -> None:
        if not tool.name.strip():
            raise ValueError("Tool name must not be empty.")
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def run_tool(self, tool_name: str, **kwargs: object) -> ToolResult:
        try:
            tool = self._tools[tool_name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {tool_name}") from exc
        return tool.run(**kwargs)

    def answer(self, question: str) -> AgentResponse:
        clean_question = question.strip()
        if not clean_question:
            raise ValueError("Question must not be empty.")

        return AgentResponse(
            question=clean_question,
            answer=(
                "Agent foundation is ready. Natural-language planning will be "
                "connected after governed tools are implemented."
            ),
        )
