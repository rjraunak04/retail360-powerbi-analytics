"""Provider-neutral orchestration layer for Retail360."""

from dataclasses import dataclass
from typing import Mapping

from .config import AgentConfig
from .planner import QueryPlan, RuleBasedPlanner
from .tools import AgentTool, ToolResult


@dataclass(frozen=True)
class AgentResponse:
    question: str
    answer: str
    intent: str = "unknown"
    plan: QueryPlan | None = None
    tool_results: tuple[ToolResult, ...] = ()


class AnalyticsAgent:
    """Plan, execute and explain governed Retail360 tool calls."""

    def __init__(
        self,
        tools: Mapping[str, AgentTool] | None = None,
        config: AgentConfig | None = None,
        planner: RuleBasedPlanner | None = None,
    ) -> None:
        self.config = config or AgentConfig()
        self._tools = dict(tools or {})
        self.planner = planner or RuleBasedPlanner()

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

    def execute_plan(self, plan: QueryPlan) -> tuple[ToolResult, ...]:
        results = []
        for step in plan.steps:
            if step.tool_name not in self._tools:
                results.append(ToolResult(tool_name=step.tool_name, ok=False, error="Required tool is not registered"))
                continue
            result = self.run_tool(step.tool_name, **step.arguments)
            results.append(result)
            if not result.ok:
                break
        return tuple(results)

    @staticmethod
    def _explain(plan: QueryPlan, results: tuple[ToolResult, ...]) -> str:
        failed = next((result for result in results if not result.ok), None)
        if failed:
            return f"Plan stopped safely because {failed.tool_name} failed: {failed.error}"

        if plan.intent == "kpi_lookup" and results and results[0].data:
            item = results[0].data[0]
            return f"{item['measure']}: {item['definition']}"

        if plan.intent in {"semantic_lookup", "discovery"} and results:
            data = results[0].data
            return (
                f"Retail360 semantic model: {data['model_name']} with "
                f"{len(data['tables'])} governed tables and "
                f"{data['relationship_count']} relationships."
            )

        return "The governed plan completed successfully."

    def answer(self, question: str) -> AgentResponse:
        clean_question = question.strip()
        if not clean_question:
            raise ValueError("Question must not be empty.")

        plan = self.planner.plan(clean_question)
        results = self.execute_plan(plan)
        return AgentResponse(
            question=clean_question,
            answer=self._explain(plan, results),
            intent=plan.intent,
            plan=plan,
            tool_results=results,
        )
