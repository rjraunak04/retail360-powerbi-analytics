# Retail360 — Stage 6 Validation Summary

## Stage

**Stage 6 — DAX KPI Layer**

## Repository implementation

Stage 6 centralizes report-facing business logic in a dedicated `Measures` table in the PBIP/TMDL semantic model.

Implemented KPI families:

- Sales & Volume
- Profitability
- Growth & Time Intelligence
- Role-Playing Dates
- Customer & Reseller
- Product
- Channel
- Promotion
- Inventory
- UX & Dynamic Titles

The semantic layer currently contains **76 explicit governed measures**.

## Modelling rules enforced

- implicit measures remain discouraged
- Gross Margin % is calculated as Gross Profit / Total Sales, not as an average of row-level percentages
- distinct orders use Channel Key + Sales Order Number
- inactive Due Date and Ship Date relationships are activated only through `USERELATIONSHIP`
- current inventory KPIs use the latest available inventory snapshot
- inventory value is not summed across historical snapshots for headline KPIs
- customer/reseller key 0 is excluded from business entity counts
- product/category contribution measures respect report selections through `ALLSELECTED`
- consolidated financial measures intentionally use neutral number formats because currency-rate history is outside the current project scope

## Repository validation gates

### SQL benchmark

`python scripts/qa_stage6_kpis.py`

This reconciles the DAX business definitions back to the PostgreSQL analytics layer, including:

- Total Sales
- Total Product Cost
- Gross Profit
- Units Sold
- Distinct Orders
- Internet + Reseller channel reconciliation
- customer/reseller/product entity counts
- repeat-customer constraints
- latest inventory snapshot
- safety-stock / reorder-point bounds
- year-level sales and profit benchmarks

### DAX contract

`python scripts/validate_stage6_dax.py`

The contract validates:

- required governed measures
- minimum measure coverage
- display folders
- weighted margin logic
- time-intelligence patterns
- inactive role-playing date usage
- latest-snapshot inventory patterns
- product contribution/ranking patterns
- PBIP Measures-table registration
- Stage 6 DAX QA mirror consistency
- currency-format policy
- runtime verifier wiring

### Power BI runtime proof

`powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage6_runtime.ps1`

The verifier connects directly to the open Retail360 Power BI Desktop semantic model and executes the Stage 6 runtime DAX contract. It writes:

`docs/data-engineering/stage6-powerbi-runtime-proof.csv`

The runtime contract contains 20 tests covering base KPI reconciliation, weighted margin, channel reconciliation, role-playing dates, promotion bounds, customer metrics, inventory snapshot metrics and time intelligence.

## Exit gate

Stage 6 is considered complete only when:

1. PostgreSQL Stage 6 KPI benchmark passes.
2. Stage 6 DAX repository contract passes.
3. PBIP scaffold validation passes.
4. PowerShell verifier scripts parse successfully.
5. GitHub Actions is green.
6. Live Power BI Desktop Stage 6 runtime QA returns **20/20 PASS**.

Until the live runtime proof is captured, repository implementation is complete but Stage 6 remains runtime-QA pending.
