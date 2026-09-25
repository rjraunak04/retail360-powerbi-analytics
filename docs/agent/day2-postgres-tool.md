# Day 2 — Safe PostgreSQL Analytics Tool

## What was added

Retail360 now has a deterministic PostgreSQL tool that sits between future
LLM reasoning and the governed `analytics` schema.

The tool is intentionally defensive:

- accepts only one `SELECT` or `WITH` statement
- rejects mutating and administrative SQL
- rejects explicit references to schemas outside `analytics`
- opens the PostgreSQL transaction in read-only mode
- applies a server-side statement timeout
- caps returned rows
- normalizes database errors into a structured `ToolResult`
- does not store database credentials in source code

## Why two safety layers?

Text validation prevents obviously unsafe requests before a database connection
is made. PostgreSQL read-only transaction mode is the second boundary. The
agent therefore does not rely on prompt instructions alone for database safety.

For deployment, the database account should also be a least-privilege,
read-only account. That is a third independent boundary.

## Example

```python
from agent.tools.postgres import PostgresAnalyticsTool

tool = PostgresAnalyticsTool()
result = tool.run(
    query="""
    SELECT product_key, SUM(sales_amount) AS total_sales
    FROM analytics.fact_sales
    GROUP BY product_key
    ORDER BY total_sales DESC
    """
)
```

The LLM/planner layer is deliberately still absent. Day 3 will add governed KPI
and semantic metadata grounding before natural-language planning is connected.
