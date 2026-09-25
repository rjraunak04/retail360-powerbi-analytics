# Day 7 - Governed Business Analysis Workflows

Day 7 moves Retail360 from metadata Q&A into controlled business analysis.

## Supported workflows

### Product sales
Ranks products by governed Total Sales.

### Channel sales
Compares sales contribution across Internet and Reseller channel grain.

### Product profitability
Ranks products using Gross Profit and calculates Gross Margin % as aggregate gross profit divided by aggregate sales. It never averages row-level margins.

### Inventory risk
Analyzes product inventory using only the global latest inventory snapshot. Historical inventory snapshots are never summed as current stock.

## Execution order

    analytical question
          |
          v
    choose approved workflow
          |
          v
    KPI grounding
          |
          v
    semantic grounding
          |
          v
    pre-defined analytical SQL
          |
          v
    Day 5 guardrails
          |
          v
    read-only PostgreSQL
          |
          v
    evidence-backed response

The planner does not generate arbitrary SQL for these workflows. It selects version-controlled analytical templates whose SQL is itself tested against the production guardrail policy.

## Design boundary

Day 7 intentionally supports a small set of high-value workflows instead of pretending to answer every possible business question. Unsupported analysis falls back to governed discovery rather than fabricated data.

Live database execution remains opt-in through the agent factory, preserving the safe local/test default.
