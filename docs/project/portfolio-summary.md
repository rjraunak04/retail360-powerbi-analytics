# Retail360 — Portfolio Summary

## One-line pitch

A source-controlled retail analytics platform that combines PostgreSQL warehouse engineering, Power BI semantic modeling, governed DAX, automated QA and a guarded analytics agent.

## What I built

I designed the project end to end: raw AdventureWorksDW extracts are validated and loaded into PostgreSQL, transformed into a governed analytics star schema, consumed by a source-controlled Power BI semantic model, exposed through 78 explicit DAX measures and ten analytical report pages, and checked through automated SQL, semantic-model, DAX, report and security validation.

I then extended the governed BI layer with an analytics agent. Instead of unrestricted text-to-SQL, the agent grounds questions in the KPI dictionary and semantic-model contract, selects approved analysis workflows, applies deterministic SQL guardrails, uses read-only PostgreSQL access and produces evidence-backed descriptive insights.

## Scale and verification

| Evidence | Result |
|---|---:|
| Harmonized sales lines | 121,253 |
| Inventory snapshot rows | 776,286 |
| Governed DAX measures | 78 |
| Exact KPI runtime checks | 34/34 |
| Measure smoke checks | 78/78 |
| Visible analytical report pages | 10 |
| Agent evaluation cases | 20 |
| Agent CI quality gate | Passing |

## Engineering decisions worth discussing

- Sales and inventory remain separate facts because they have different grains.
- Gross Margin % is calculated as weighted Gross Profit / Total Sales.
- Distinct orders use Channel + Sales Order Number to avoid cross-channel collisions.
- Current inventory uses the latest snapshot instead of summing historical snapshots.
- Negative historical inventory is preserved and validated rather than silently rewritten.
- Promotion analysis remains descriptive; the project does not claim causal lift.
- The analytics agent uses deterministic governance and evaluation before optional LLM expansion.

## Reviewer path

1. [README](../../README.md) — project overview and architecture
2. [Dashboard gallery](../screenshots/README.md) — real Power BI output
3. [KPI dictionary](../powerbi/kpi-dictionary.md) — governed metric definitions
4. [Architecture](../architecture/retail360-architecture.md) — warehouse and BI design
5. [Agent recruiter guide](../agent/recruiter-guide.md) — agent design and demo
6. [Validation evidence](../data-engineering/stage8-validation-summary.md) — runtime QA evidence

## Interview positioning

This is not only a Power BI dashboard. It demonstrates data ingestion, PostgreSQL modeling, dimensional design, Power Query, semantic modeling, DAX governance, BI UX, QA automation, source control, CI and applied agent engineering in one coherent analytics system.
