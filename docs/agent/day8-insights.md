# Day 8 - Automated Insight Engine

Day 8 converts governed query results into deterministic business observations.

## Insight types

The engine can produce:

- top-product contributor observations
- returned-set concentration flags
- channel leader observations
- gross-profit leader observations
- negative-profit flags
- non-positive latest-inventory flags
- lowest-inventory observations

## Evidence contract

Every insight contains:

- a machine-readable kind
- a human-readable message
- structured evidence used for the statement

This allows UI, API or later LLM layers to consume the same evidence without recomputing business logic.

## No unsupported causality

The insight engine describes what is present in the governed result set. It does not claim why a metric moved and does not convert correlation into causation.

For example:

- allowed: "Reseller has the highest sales among returned channels."
- not allowed: "Reseller strategy caused sales growth."

## Scope-aware concentration

Product concentration is explicitly calculated from the returned ranked set and labelled as such. It is not presented as share of all company sales unless the query result actually represents the complete denominator.

## Inventory semantics

Inventory flags retain the project's latest-snapshot rule. Historical snapshots are not interpreted as current stock.

## Flow

    governed workflow
          |
          v
    read-only result rows
          |
          v
    deterministic insight rules
          |
          +--> structured evidence
          |
          +--> human-readable observations
          |
          v
    AgentResponse.insights

The engine remains provider-neutral and requires no external LLM or API.
