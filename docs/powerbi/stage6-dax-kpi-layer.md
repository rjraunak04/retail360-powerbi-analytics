# Stage 6 — DAX KPI Layer

## Status

Repository implementation complete. Live Power BI runtime verification is performed with `Stage6 KPI QA.dax`.

## Design

A dedicated calculated table named `Measures` hosts all report-facing KPIs. The table contains a single hidden dummy column and is excluded from business analysis except as a measure container.

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

The runtime QA contains 20 reconciliation and bounded-value tests.
