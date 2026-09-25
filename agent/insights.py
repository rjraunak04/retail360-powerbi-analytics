"""Deterministic insight generation from governed workflow results."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
from typing import Any


@dataclass(frozen=True)
class Insight:
    kind: str
    message: str
    evidence: dict[str, Any]


def _numeric(value: Any) -> float | None:
    return float(value) if isinstance(value, Number) else None


def generate_insights(workflow: str, rows: list[dict[str, Any]]) -> tuple[Insight, ...]:
    """Create descriptive, evidence-backed observations without causal claims."""

    if not rows:
        return ()

    insights: list[Insight] = []

    if workflow == "product_sales":
        top = rows[0]
        total = sum(_numeric(row.get("total_sales")) or 0.0 for row in rows)
        top_sales = _numeric(top.get("total_sales")) or 0.0
        share = top_sales / total if total else 0.0
        insights.append(Insight(
            "top_contributor",
            f"{top.get('product_name')} is the top product in the returned ranking.",
            {"total_sales": top_sales, "share_of_returned_sales": share},
        ))
        if share >= 0.30:
            insights.append(Insight(
                "concentration",
                "The leading product contributes at least 30% of sales within the returned top-product set.",
                {"share_of_returned_sales": share, "scope": "returned rows only"},
            ))

    elif workflow == "channel_sales":
        ordered = sorted(rows, key=lambda row: _numeric(row.get("total_sales")) or 0.0, reverse=True)
        top = ordered[0]
        total = sum(_numeric(row.get("total_sales")) or 0.0 for row in ordered)
        share = (_numeric(top.get("total_sales")) or 0.0) / total if total else 0.0
        insights.append(Insight(
            "channel_leader",
            f"{top.get('channel_name')} has the highest sales among returned channels.",
            {"share_of_returned_sales": share},
        ))

    elif workflow == "product_profitability":
        top = rows[0]
        insights.append(Insight(
            "profit_leader",
            f"{top.get('product_name')} leads the returned products by gross profit.",
            {
                "gross_profit": _numeric(top.get("gross_profit")),
                "gross_margin_pct": _numeric(top.get("gross_margin_pct")),
            },
        ))
        negative = [row for row in rows if (_numeric(row.get("gross_profit")) or 0.0) < 0]
        if negative:
            insights.append(Insight(
                "negative_profit_flag",
                f"{len(negative)} returned product(s) have negative gross profit.",
                {"product_count": len(negative)},
            ))

    elif workflow == "inventory_risk":
        non_positive = [
            row for row in rows
            if (_numeric(row.get("current_inventory_units")) or 0.0) <= 0
        ]
        if non_positive:
            insights.append(Insight(
                "inventory_attention",
                f"{len(non_positive)} returned product(s) have non-positive units at the latest snapshot.",
                {"product_count": len(non_positive), "scope": "latest snapshot"},
            ))
        lowest = rows[0]
        insights.append(Insight(
            "lowest_inventory",
            f"{lowest.get('product_name')} has the lowest units in the returned inventory ranking.",
            {"current_inventory_units": _numeric(lowest.get("current_inventory_units"))},
        ))

    return tuple(insights)
