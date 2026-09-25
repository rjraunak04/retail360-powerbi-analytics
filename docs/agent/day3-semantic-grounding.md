# Day 3 - KPI and Semantic Grounding

Day 3 gives the future planner a governed business vocabulary before natural-language planning is connected.

## KPI metadata

The KPI tool reads the existing canonical KPI dictionary rather than duplicating business rules inside prompts. This preserves important semantics such as weighted Gross Margin %, collision-safe Distinct Orders, latest-snapshot inventory, descriptive-only promotion analysis, and currency-neutral consolidated monetary values.

## Semantic metadata

The semantic tool reads the existing Power BI semantic-model contract. It exposes model and source information, table-to-PostgreSQL mappings, columns, relationships, and active or inactive role-playing dates.

## Grounding flow

    Business question
          |
          v
    KPI definition lookup
          |
          v
    Semantic metadata lookup
          |
          v
    Safe PostgreSQL execution
          |
          v
    Evidence-backed explanation

This is stronger than generic text-to-SQL because syntactically correct SQL can still violate business definitions. Retail360 now separates business meaning, semantic mapping, safe execution, and explanation.
