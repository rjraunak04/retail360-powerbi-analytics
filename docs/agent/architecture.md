# Retail360 Analytics Agent — Architecture

## Goal

Add a governed natural-language analytics layer to Retail360 without replacing
the warehouse, semantic model, DAX layer, or existing QA gates.

The agent is an orchestration layer, not a second source of business logic.

## Design principles

1. **Governed metrics first** — reuse Retail360 definitions instead of asking an
   LLM to invent KPI logic.
2. **Deterministic tools** — database access, metadata lookup, and validation
   live behind explicit tool contracts.
3. **Read-only by default** — analytics queries must not mutate the warehouse.
4. **Evidence before explanation** — business answers should be backed by tool
   results and, where applicable, existing QA baselines.
5. **Provider-neutral core** — the orchestration package is not coupled to one
   LLM vendor.
6. **Incremental complexity** — start with one orchestrator and multiple tools;
   add specialized agents only when evaluation demonstrates a real need.

## Target flow

    Business question
          |
          v
    AnalyticsAgent
          |
          +--> KPI / metadata tool
          +--> read-only PostgreSQL tool
          +--> semantic-model tool
          +--> QA / validation tool
          |
          v
    grounded result + evidence + explanation

## Safety boundary

The future PostgreSQL tool will allow only read-only analytical access to the
approved analytics schema, apply row limits and timeouts, and reject mutating
statements. Credentials remain outside source control.

## Delivery stages

- Stage A: provider-neutral agent foundation and tool contracts
- Stage B: safe PostgreSQL analytics tool
- Stage C: KPI and semantic metadata grounding
- Stage D: LLM planning/orchestration
- Stage E: benchmark questions and automated evaluation
- Stage F: CI, documentation, and recruiter demo
