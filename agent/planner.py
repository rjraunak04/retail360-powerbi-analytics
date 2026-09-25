"""Deterministic planning for the Retail360 analytics agent."""

from dataclasses import dataclass

from .workflows import choose_workflow


@dataclass(frozen=True)
class PlanStep:
    tool_name: str
    arguments: dict[str, object]
    purpose: str


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    steps: tuple[PlanStep, ...]


class RuleBasedPlanner:
    """Small auditable planner used before an external LLM is introduced."""

    def plan(self, question: str) -> QueryPlan:
        text = question.casefold()
        workflow = choose_workflow(question)
        if workflow:
            return QueryPlan(
                intent="business_analysis",
                steps=(
                    PlanStep("kpi_metadata", {"query": workflow.metric}, "Ground the workflow metric"),
                    PlanStep("semantic_metadata", {"action": "summary"}, "Ground the workflow in the semantic model"),
                    PlanStep(
                        "postgres_analytics",
                        {"query": workflow.query, "workflow": workflow.name},
                        workflow.interpretation,
                    ),
                ),
            )

        if any(word in text for word in ("schema", "table", "column", "relationship", "model")):
            return QueryPlan(
                intent="semantic_lookup",
                steps=(PlanStep("semantic_metadata", {"action": "summary"}, "Inspect governed model metadata"),),
            )

        kpi_terms = {
            "sales": "Total Sales",
            "revenue": "Total Sales",
            "margin": "Gross Margin %",
            "profit": "Gross Profit",
            "inventory": "Current Inventory Value / Units",
            "orders": "Distinct Orders",
            "units": "Units Sold",
        }
        metric = next((value for key, value in kpi_terms.items() if key in text), None)
        if metric:
            return QueryPlan(
                intent="kpi_lookup",
                steps=(
                    PlanStep("kpi_metadata", {"query": metric}, "Ground the metric in the KPI dictionary"),
                    PlanStep("semantic_metadata", {"action": "summary"}, "Ground the metric in the semantic model"),
                ),
            )

        return QueryPlan(
            intent="discovery",
            steps=(PlanStep("semantic_metadata", {"action": "summary"}, "Inspect available governed analytics metadata"),),
        )
