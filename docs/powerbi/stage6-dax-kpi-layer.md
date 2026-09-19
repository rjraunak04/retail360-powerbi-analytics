# Stage 6 — DAX KPI Layer

## Status

Repository implementation and PostgreSQL benchmark reconciliation are complete. Live Power BI runtime verification remains the final exit gate.

## Design

A dedicated calculated table named `KPI_Measures` hosts **78 governed report-facing measures**. The table contains a single hidden dummy column and is excluded from business analysis except as a measure container.

The host is intentionally named `KPI_Measures` because `Measures` is a reserved/unsupported Power BI table name in current Desktop/PBIP builds. It uses a one-row static M partition instead of a calculated-table partition, avoiding semantic-model calculation dependencies during load.\n\nThe layer covers:

- sales and volume
- profitability
- MTD/QTD/YTD and prior-period growth
- role-playing Due/Ship dates
- customer and reseller KPIs
- product contribution and ranking
- Internet/Reseller channel mix
- discount/promotion analysis
- latest-snapshot inventory analytics
- dynamic period/title text

## Governing rules

- report visuals should use explicit measures
- Gross Margin % = SUM(Gross Profit) / SUM(Sales), never an average of row percentages
- distinct orders use Channel + Sales Order Number
- customer/reseller counts exclude warehouse key 0
- inventory headlines use the latest snapshot
- currency symbols are not attached to consolidated totals until currency conversion semantics are implemented

## Validation

Repository validation:

`python scripts/validate_stage6_dax.py`

Live Power BI QA:

`powerbi/Retail360.SemanticModel/DAXQueries/Stage6 KPI QA.dax`

The runtime gate contains 34 exact reconciliation, role-date, customer, channel, inventory, and time-intelligence checks plus a 78-measure live smoke suite. The one-command full gate is `scripts/verify_powerbi_stage6_runtime.ps1`.


## Repository benchmark

GitHub Actions independently rebuilds the analytics schema and verifies the KPI layer against PostgreSQL. Important reference values include 109,809,274.2030 Total Sales, 12,551,366.2483 Gross Profit, 18,484 customers, 635 resellers, a 2014-06-30 latest inventory snapshot, and 23,603,975.5700 Current Inventory Value.

See `docs/data-engineering/stage6-validation-summary.md` for the complete evidence table.


## Load-stability hardening

- `KPI_Measures` uses a one-row static M table so the measure host does not participate in calculated-table dependency evaluation.
- All 12 source tables now use the exact Stage 5 navigator-based PostgreSQL import pattern that already passed the live 20/20 Power BI runtime gate. Stage 6 therefore changes semantic logic only; it no longer experiments with source-partition loading behavior.

## Why Stage 6 surfaced several runtime issues

Stage 5 had already proven the PostgreSQL source partitions and star schema in a live Power BI runtime. Most Stage 6 failures were therefore integration regressions around the new semantic layer and validation tooling rather than bad source data.

The hardened design now follows these rules:

- keep the 12 source-table partitions identical to the Stage 5 runtime-proven baseline
- add Stage 6 business logic only through the `KPI_Measures` host and DAX queries
- use a static one-row M partition for `KPI_Measures` so the measure host does not create calculated-table load dependencies
- never launch duplicate Power BI runtime copies during verification
- clean only repository-local Power BI caches on a cold start
- fail fast when multiple Power BI Desktop instances are running, because parallel semantic-model engines can trigger memory pressure and misleading provider/container errors
- validate the final model through 34 exact KPI checks and a 78-measure smoke suite
