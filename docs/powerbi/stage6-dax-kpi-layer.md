# Stage 6 — DAX KPI Layer

## Status

Repository implementation and PostgreSQL benchmark reconciliation are complete. Live Power BI runtime verification remains the final exit gate.

## Design

A dedicated calculated table named `Measures` hosts **78 governed report-facing measures**. The table contains a single hidden dummy column and is excluded from business analysis except as a measure container.

The layer covers:

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
