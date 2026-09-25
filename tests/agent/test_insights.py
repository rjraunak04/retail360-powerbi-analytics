from agent.insights import generate_insights


def test_product_sales_generates_top_contributor_and_concentration():
    rows = [
        {"product_name": "A", "total_sales": 60.0},
        {"product_name": "B", "total_sales": 25.0},
        {"product_name": "C", "total_sales": 15.0},
    ]
    insights = generate_insights("product_sales", rows)
    assert insights[0].kind == "top_contributor"
    assert insights[0].evidence["share_of_returned_sales"] == 0.60
    assert any(item.kind == "concentration" for item in insights)


def test_channel_insight_is_descriptive():
    rows = [
        {"channel_name": "Reseller", "total_sales": 80.0},
        {"channel_name": "Internet", "total_sales": 20.0},
    ]
    insight = generate_insights("channel_sales", rows)[0]
    assert insight.kind == "channel_leader"
    assert "highest sales" in insight.message
    assert "caused" not in insight.message.casefold()


def test_profitability_flags_negative_profit():
    rows = [
        {"product_name": "A", "gross_profit": 10.0, "gross_margin_pct": 0.2},
        {"product_name": "B", "gross_profit": -2.0, "gross_margin_pct": -0.1},
    ]
    insights = generate_insights("product_profitability", rows)
    assert any(item.kind == "negative_profit_flag" for item in insights)


def test_inventory_uses_latest_snapshot_language():
    rows = [
        {"product_name": "A", "current_inventory_units": -2, "current_inventory_value": -20.0},
        {"product_name": "B", "current_inventory_units": 3, "current_inventory_value": 30.0},
    ]
    insights = generate_insights("inventory_risk", rows)
    flag = next(item for item in insights if item.kind == "inventory_attention")
    assert flag.evidence["scope"] == "latest snapshot"
    assert "non-positive" in flag.message


def test_empty_results_do_not_invent_insights():
    assert generate_insights("product_sales", []) == ()


def test_concentration_claim_is_scoped_to_returned_rows():
    rows = [
        {"product_name": "A", "total_sales": 70.0},
        {"product_name": "B", "total_sales": 30.0},
    ]
    insight = next(item for item in generate_insights("product_sales", rows) if item.kind == "concentration")
    assert insight.evidence["scope"] == "returned rows only"
