from agent.tools.kpi import KpiMetadataTool, load_kpis
from agent.tools.metadata import SemanticMetadataTool


def test_core_kpis_are_parsed():
    kpis = load_kpis()
    assert "Total Sales" in kpis
    assert "Gross Margin %" in kpis
    assert "weighted margin" in kpis["Gross Margin %"]["definition"]


def test_kpi_exact_lookup():
    result = KpiMetadataTool().run(query="Gross Margin %")
    assert result.ok is True
    assert result.data[0]["section"] == "Profitability"


def test_inventory_snapshot_semantics():
    result = KpiMetadataTool().run(query="Current Inventory Value / Units")
    assert result.ok is True
    assert "latest snapshot" in result.data[0]["definition"]


def test_semantic_summary():
    result = SemanticMetadataTool().run(action="summary")
    assert result.ok is True
    assert result.data["model_name"] == "Retail360"
    assert result.data["source"]["schema"] == "analytics"
    assert result.data["relationship_count"] == 14


def test_fact_sales_mapping():
    result = SemanticMetadataTool().run(action="table", table="FactSales")
    columns = {column[0]: column[1] for column in result.data["columns"]}
    assert columns["Sales Amount"] == "sales_amount"
    assert columns["Gross Profit"] == "gross_profit"


def test_role_playing_dates():
    result = SemanticMetadataTool().run(action="relationships", table="DimDate")
    relationships = {item["name"]: item for item in result.data}
    assert relationships["Sales_OrderDate"]["active"] is True
    assert relationships["Sales_DueDate"]["active"] is False
    assert relationships["Sales_ShipDate"]["active"] is False
