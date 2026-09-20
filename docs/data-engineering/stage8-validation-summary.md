# Retail360 — Stage 8 Validation Summary

## Stage

**Stage 8 — Enterprise Features and QA**

## Security / RLS

Three static demonstration roles are source-controlled in TMDL:

- `RLS_North_America`
- `RLS_Europe`
- `RLS_Pacific`

Each role restricts `DimSalesTerritory[Territory Group]` and denies `FactInventory` rows because the inventory fact has no territory grain. Role membership is intentionally not committed.

SQL-derived regional baselines:

| Territory group | Sales lines | Orders | Sales |
|---|---:|---:|---:|
| North America | 79,217 | 16,108 | 79,353,361.1796 |
| Europe | 26,978 | 8,504 | 19,800,577.0623 |
| Pacific | 15,058 | 6,843 | 10,655,335.9611 |
| **Total** | **121,253** | — | **109,809,274.2030** |

The three regional sales totals reconcile exactly to the global sales total.

## Relationship QA

The model remains a conventional star schema with 14 relationships:

- FactSales → conformed dimensions
- FactInventory → Product and Date
- Order Date active
- Due Date inactive
- Ship Date inactive
- no bidirectional relationships
- no relationship to the `KPI_Measures` host

## DAX optimization review

The Stage 8 contract keeps the 78-measure governed KPI layer and validates:

- weighted gross margin
- `DIVIDE` for high-risk ratio measures
- role-playing date activation through `USERELATIONSHIP`
- selection-aware ranking/contribution with `ALLSELECTED`
- latest-snapshot inventory variables
- no averaging of row-level margin percentages
- no broad `FILTER(FactSales,...)` iterator pattern
- no consolidated currency symbol while currency conversion is out of scope

Known higher-cost measures such as composite distinct orders, ranking and product-level inventory-risk iterators are documented and intentionally retained because they are semantically correct.

## Edge-case QA

The Stage 8 SQL suite covers fact grains, key integrity, quantity/value ranges, profit/margin arithmetic, date ordering, channel applicability, inventory grain/date arithmetic and RLS territory reconciliation.

A source-level inventory edge case is explicitly preserved: **3,319 historical inventory snapshots have negative units balance and correspondingly negative inventory value**. Stage 8 does not silently rewrite these rows. Instead it validates that inventory value arithmetic remains consistent and that unit cost itself is not negative.

## Report performance review

The Stage 7 report baseline remains:

- 10 visible pages
- 1 hidden tooltip page
- 62 visual containers total
- maximum 6 visuals on a visible page
- native visual types only
- explicit semantic measures

This structural performance contract is CI-enforced. Desktop Performance Analyzer capture remains an environment evidence step and is documented separately.

## Refresh and deployment

Stage 8 documents:

- local Docker/PostgreSQL refresh order
- least-privilege Power BI database access
- gateway/cloud PostgreSQL options for Power BI Service
- parameterized `pServer` / `pDatabase`
- PBIP as the canonical source-controlled artifact
- PBIX as an optional distribution/demo artifact
- no committed credentials or machine-local cache/runtime files

## Automated gates

CI runs:

- Stage 1 source integrity
- Stage 2 raw warehouse QA
- Stage 3 staging QA
- Stage 4 analytics QA
- Stage 5 semantic/PBIP validation
- Stage 6 KPI SQL/DAX validation
- Stage 7 PBIR UX validation
- Stage 8 SQL edge-case QA
- Stage 8 enterprise semantic/performance contract
- PowerShell parser validation for Stage 5, Stage 6 and Stage 8 runtime gates

A local optional runtime gate is available at:

`scripts/verify_powerbi_stage8_runtime.ps1`

It reruns the Stage 6 semantic-model regression gate and validates all three RLS roles through the live Power BI local Analysis Services engine.


## Stage 6 runtime reuse policy

Stage 8 reuses a single healthy open Retail360 Power BI Desktop instance for the Stage 6 regression gate. It does **not** force-close and reopen Desktop on every Stage 8 run. The Stage 6 live DAX gates still prove that the loaded semantic model is the expected current model through 34 exact KPI checks and the 78-measure smoke suite. A clean start is used only when no Power BI Desktop instance is running or when explicitly requested for diagnostics.


## Local RLS runtime implementation

Local Power BI Desktop runtime QA does not impersonate a role through the MSOLAP `Roles` connection-string property. Instead, Stage 8 combines:

- static validation of the exact TMDL role expressions,
- live DAX execution of the same territory filter semantics,
- exact reconciliation to PostgreSQL regional baselines,
- fail-closed inventory semantics in the live DAX checks.

This design is deterministic on a normal Desktop workstation and avoids a false failure caused by administrative impersonation requirements on the local Analysis Services endpoint. Interactive **View As** / Power BI Service **Test as role** remains the final identity-assignment check.
