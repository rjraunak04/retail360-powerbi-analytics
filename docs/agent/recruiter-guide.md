# Retail360 Agent — Recruiter Guide

Retail360 extends a production-style BI stack with a governed analytics agent. The agent is deliberately not a generic chatbot: business definitions, semantic metadata, SQL safety, analytical workflows, insight rules and evaluation are version controlled and independently testable.

## 30-second explanation

I built Retail360 as an end-to-end retail analytics platform using PostgreSQL and Power BI. I then added an agentic analytics layer that grounds questions in the existing KPI dictionary and semantic model, uses read-only guarded PostgreSQL access, selects approved business-analysis workflows, generates evidence-backed descriptive insights, and is regression-tested through a benchmark and GitHub Actions.

## What makes the agent different

- KPI definitions come from the same governed dictionary used by the BI model.
- Semantic mappings come from the source-controlled Power BI model contract.
- SQL execution is deterministic, read-only and allow-listed.
- High-value analysis uses tested workflow templates rather than unrestricted text-to-SQL.
- Insights retain denominator/snapshot scope and avoid unsupported causal claims.
- A version-controlled benchmark measures intent, tool routing, grounding and answer evidence.
- CI fails when measured quality falls below the baseline.

## Demo

Run the metadata-only demo without PostgreSQL:

    python scripts/demo_agent.py

Run the deterministic evaluation:

    python -m agent.evaluation.evaluate

Run all agent tests:

    pytest -q tests/agent

Database-backed business workflows are intentionally opt-in:

    from agent import build_default_agent
    agent = build_default_agent(include_database=True)
    response = agent.answer("Show top products by sales")

The local Retail360 PostgreSQL warehouse must be running for database-backed analysis.

## Interview architecture

    Question
       |
       v
    Planner
       |
       +--> KPI dictionary
       |
       +--> Semantic contract
       |
       v
    Governed workflow
       |
       v
    SQL guardrails
       |
       v
    Read-only PostgreSQL
       |
       v
    Evidence rows
       |
       v
    Deterministic insights
       |
       v
    Grounded response

## Key trade-off

I chose a deterministic planner and approved workflow templates before adding an external LLM. That gives the project a measurable safety and quality baseline. A future LLM can improve language understanding while the deterministic controls remain authoritative.

## Scope

Implemented: grounding, planning, safe SQL boundary, governed workflows, automated insights, evaluation and CI.

Not claimed: autonomous database mutation, unrestricted text-to-SQL, causal inference from descriptive sales data, or production cloud deployment without environment evidence.
