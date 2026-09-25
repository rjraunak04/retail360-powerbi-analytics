from agent.factory import build_default_agent
from agent.planner import RuleBasedPlanner


def test_planner_routes_margin_to_governed_kpi():
    plan = RuleBasedPlanner().plan("What is our gross margin?")
    assert plan.intent == "kpi_lookup"
    assert plan.steps[0].tool_name == "kpi_metadata"
    assert plan.steps[0].arguments["query"] == "Gross Margin %"


def test_planner_routes_inventory_to_snapshot_kpi():
    plan = RuleBasedPlanner().plan("Explain current inventory")
    assert plan.steps[0].arguments["query"] == "Current Inventory Value / Units"


def test_default_agent_answers_from_governed_definition():
    agent = build_default_agent()
    response = agent.answer("What is gross margin?")
    assert response.intent == "kpi_lookup"
    assert "Gross Margin %" in response.answer
    assert "weighted margin" in response.answer
    assert all(result.ok for result in response.tool_results)


def test_default_agent_can_explain_semantic_model():
    agent = build_default_agent()
    response = agent.answer("Explain the semantic model schema")
    assert response.intent == "semantic_lookup"
    assert "14 relationships" in response.answer


def test_database_tool_is_opt_in():
    agent = build_default_agent()
    assert "postgres_analytics" not in agent.tool_names


def test_unknown_registered_tool_failure_stops_safely():
    agent = build_default_agent()
    plan = RuleBasedPlanner().plan("What is gross margin?")
    agent._tools.pop("kpi_metadata")
    results = agent.execute_plan(plan)
    assert results[0].ok is False
    assert "not registered" in results[0].error
