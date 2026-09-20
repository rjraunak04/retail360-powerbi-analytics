# Retail360 — Stage 8 Enterprise Features and QA

## Scope

Stage 8 hardens the completed warehouse, semantic model and report for enterprise-style review.

Implemented gates:

- territory RLS design
- relationship-model QA
- DAX optimization contract
- PostgreSQL KPI and edge-case reconciliation
- report performance-structure review
- refresh/deployment guidance
- PBIP/PBIX source-control strategy

## Automated SQL / edge-case QA

Run:

`python scripts/qa_stage8_enterprise.py`

The test suite validates:

- sales and inventory fact row counts
- duplicate fact grains
- broken core foreign keys
- nonpositive quantities and negative sales
- gross-profit and gross-margin arithmetic
- order/due/ship date ordering
- channel applicability rules
- inventory grain/date/value sanity
- absence of a territory key from the inventory grain
- presence of North America / Europe / Pacific RLS regions
- reconciliation of regional sales back to global sales

The script also writes a local RLS baseline to:

`.runtime/stage8-rls-baseline.json`

## Static enterprise contract

Run:

`python scripts/validate_stage8_enterprise.py`

This checks the three RLS role files, role registration, relationship direction, inactive date roles, DAX performance patterns, report visual density and required deployment documentation.

## Relationship QA policy

The semantic model must remain a star schema:

- 14 relationships total
- facts on the many side and dimensions on the one side
- Order Date active
- Due Date and Ship Date inactive
- no bidirectional relationship
- no relationship to the `KPI_Measures` host

## Exit gate

Stage 8 repository work is complete only when the full GitHub CI pipeline passes all Stage 1–8 validations. Local Power BI Service assignment and Desktop Performance Analyzer captures are environment evidence, not source-control prerequisites.
