from agent.planner import RuleBasedPlanner
from agent.workflows import WORKFLOWS, choose_workflow
from agent.guardrails import SqlGuardrailPolicy, validate_agent_sql


def test_product_sales_workflow_selection():
    workflow = choose_workflow("Show top products by sales")
    assert workflow.name == "product_sales"
    assert workflow.metric == "Total Sales"


def test_channel_sales_workflow_selection():
    assert choose_workflow("Compare sales by channel").name == "channel_sales"


def test_product_profitability_uses_weighted_margin():
    workflow = choose_workflow("Rank products by profit and margin")
    assert workflow.name == "product_profitability"
    assert "SUM(f.gross_profit) / SUM(f.sales_amount)" in workflow.query


def test_inventory_workflow_uses_latest_snapshot():
    workflow = choose_workflow("Analyze lowest inventory products")
    assert workflow.name == "inventory_risk"
    assert "MAX(date_key)" in workflow.query


def test_analysis_plan_grounds_before_database_execution():
    plan = RuleBasedPlanner().plan("Show top products by sales")
    assert plan.intent == "business_analysis"
    assert [step.tool_name for step in plan.steps] == [
        "kpi_metadata",
        "semantic_metadata",
        "postgres_analytics",
    ]


def test_all_workflow_sql_passes_production_guardrails():
    policy = SqlGuardrailPolicy(
        allowed_schema="analytics",
        allowed_tables=frozenset({
            "fact_sales", "fact_inventory", "dim_product", "dim_channel"
        }),
    )
    for workflow in WORKFLOWS.values():
        assert validate_agent_sql(workflow.query, policy)
