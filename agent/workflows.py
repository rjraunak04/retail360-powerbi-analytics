"""Deterministic business-analysis workflows for Retail360."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisWorkflow:
    name: str
    metric: str
    grain: str
    query: str
    interpretation: str


WORKFLOWS = {
    "product_sales": AnalysisWorkflow(
        name="product_sales",
        metric="Total Sales",
        grain="Product",
        query="""SELECT p.product_name, SUM(f.sales_amount) AS total_sales
FROM analytics.fact_sales f
JOIN analytics.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 10""",
        interpretation="Ranks products by governed sales amount.",
    ),
    "channel_sales": AnalysisWorkflow(
        name="channel_sales",
        metric="Total Sales",
        grain="Channel",
        query="""SELECT c.channel_name, SUM(f.sales_amount) AS total_sales
FROM analytics.fact_sales f
JOIN analytics.dim_channel c ON c.channel_key = f.channel_key
GROUP BY c.channel_name
ORDER BY total_sales DESC""",
        interpretation="Compares sales contribution across governed channels.",
    ),
    "product_profitability": AnalysisWorkflow(
        name="product_profitability",
        metric="Gross Profit",
        grain="Product",
        query="""SELECT p.product_name, SUM(f.gross_profit) AS gross_profit,
SUM(f.sales_amount) AS total_sales,
CASE WHEN SUM(f.sales_amount) = 0 THEN NULL
ELSE SUM(f.gross_profit) / SUM(f.sales_amount) END AS gross_margin_pct
FROM analytics.fact_sales f
JOIN analytics.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_name
ORDER BY gross_profit DESC
LIMIT 10""",
        interpretation="Uses weighted gross margin: total gross profit divided by total sales.",
    ),
    "inventory_risk": AnalysisWorkflow(
        name="inventory_risk",
        metric="Current Inventory Value / Units",
        grain="Product",
        query="""WITH latest AS (
SELECT MAX(date_key) AS date_key FROM analytics.fact_inventory
)
SELECT p.product_name, SUM(i.units_balance) AS current_inventory_units,
SUM(i.inventory_value) AS current_inventory_value
FROM analytics.fact_inventory i
JOIN latest l ON l.date_key = i.date_key
JOIN analytics.dim_product p ON p.product_key = i.product_key
GROUP BY p.product_name
ORDER BY current_inventory_units ASC
LIMIT 20""",
        interpretation="Uses only the global latest inventory snapshot; historical snapshots are not summed.",
    ),
}


def choose_workflow(question: str) -> AnalysisWorkflow | None:
    text = question.casefold()
    analytical = any(term in text for term in ("top", "compare", "rank", "breakdown", "by ", "perform", "analysis", "analyze", "lowest", "highest"))
    if not analytical:
        return None
    if "inventory" in text:
        return WORKFLOWS["inventory_risk"]
    if ("profit" in text or "margin" in text) and "product" in text:
        return WORKFLOWS["product_profitability"]
    if "channel" in text and ("sales" in text or "revenue" in text):
        return WORKFLOWS["channel_sales"]
    if "product" in text and ("sales" in text or "revenue" in text):
        return WORKFLOWS["product_sales"]
    return None
