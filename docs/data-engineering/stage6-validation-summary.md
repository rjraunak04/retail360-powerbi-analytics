# Stage 6 — DAX KPI Layer Validation Summary

## Status

Stage 6 is COMPLETE. Repository implementation, PostgreSQL benchmark reconciliation, live Power BI exact KPI reconciliation (34/34), and the 78/78 all-measure smoke suite have passed.

## Governed semantic layer

Stage 6 provides a dedicated `KPI_Measures` table with **78 explicit report-facing measures** across:

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

The semantic model discourages implicit measures. Technical fact columns remain hidden so report authors consume governed measures.

## PostgreSQL benchmark proof

GitHub Actions rebuilds the warehouse from the official source files and reconciles the Stage 6 KPI benchmarks directly against the `analytics` schema.

Verified benchmark values:

| KPI | PostgreSQL benchmark |
|---|---:|
| Total Sales | 109,809,274.2030 |
| Total Product Cost | 97,257,907.9547 |
| Gross Profit | 12,551,366.2483 |
| Units Sold | 274,776 |
| Distinct Orders | 31,455 |
| Customers | 18,484 |
| Repeat Customers | 6,865 |
| Resellers | 635 |
| Products Sold | 350 |
| Internet Sales | 29,358,677.2207 |
| Reseller Sales | 80,450,596.9823 |
| Discounted Sales | 5,422,689.0264 |
| Latest Inventory Date | 2014-06-30 |
| Current Inventory Value | 23,603,975.5700 |
| Current Inventory Units | 258,981 |
| Products With Inventory | 606 |
| Products Below Safety Stock | 543 |
| Products Below Reorder Point | 0 |
| Sales 2013 | 49,926,384.4972 |
| Sales 2014 | 45,694.7200 |
| Due-date Sales 2013 | 52,285,231.9952 |
| Ship-date Sales 2013 | 52,522,104.8347 |
| Gross Profit 2013 | 6,273,540.9644 |
| Gross Profit 2014 | 25,552.9376 |

## DAX policy checks

Repository validation enforces:

- weighted `Gross Margin % = Gross Profit / Total Sales`
- MTD/QTD/YTD and prior-year patterns against `DimDate[Date]`
- inactive Due Date and Ship Date activation with `USERELATIONSHIP`
- selection-aware product/category contribution and ranking
- latest-snapshot inventory logic
- neutral numeric currency formatting because no exchange-rate fact is in scope
- one display-folder assignment for every governed measure
- synchronized source and PBIP runtime QA files
- exactly **34 live exact runtime checks**

## Runtime gate

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage6_runtime.ps1
```

The script performs four gates in sequence:

1. PostgreSQL KPI reconciliation
2. DAX/TMDL contract validation
3. live Power BI exact KPI reconciliation (34 checks)
4. live Power BI all-measure smoke validation (78 measures)

The local verifier writes temporary evidence under the ignored `.runtime/` directory:

- `.runtime/stage6-powerbi-runtime-proof.csv`
- `.runtime/stage6-measure-smoke-proof.csv`

Reviewed canonical runtime evidence is committed under `docs/data-engineering/`: `stage6-powerbi-runtime-proof.csv` and `stage6-measure-smoke-proof.csv`. Both exit gates are satisfied: **34/34 exact KPI checks PASS** and **78/78 governed measures evaluate successfully**.


## Load-stability hardening

- `KPI_Measures` uses a one-row static M table so the measure host does not participate in calculated-table dependency evaluation.
- All 12 source tables now use the exact Stage 5 navigator-based PostgreSQL import pattern that already passed the live 20/20 Power BI runtime gate. Stage 6 therefore changes semantic logic only; it no longer experiments with source-partition loading behavior.


## Stage 6 stability reset — final architecture

The repeated Desktop errors were not caused by incorrect KPI mathematics or broken PostgreSQL facts. They were integration failures at the PBIP/Power Query/Desktop runtime boundary.

Final hardening decisions:

- all **12 imported semantic tables** use the exact Stage 5 navigator-based PostgreSQL import pattern that already passed live 20/20 Power BI runtime QA
- Stage 6 does not alter the proven source-partition layer; it adds semantic business logic only
- `KPI_Measures` is a static one-row M host, not a DAX calculated table
- the Stage 6 verifier uses **one Power BI model instance** and no longer opens a second temporary PBIP model on every run
- orphaned temporary runtime instances from older verifier versions are cleaned before QA
- PBIP validation fails if the source partitions drift away from the Stage 5 runtime-proven pattern
- runtime QA remains 34 exact KPI reconciliations + 78 measure smoke checks

This design minimizes the Stage 6 change surface and prevents repeated verifier runs from multiplying local Analysis Services memory usage.


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


## Final live Power BI runtime proof

**Status: PASSED — 20 September 2026**

The canonical Retail360 PBIP project was validated against the live local Power BI Desktop semantic model after PostgreSQL and repository contracts had already passed.

Final live results:

- Stage 6 SQL KPI benchmark: **PASS**
- Stage 6 DAX/TMDL contract: **PASS**
- governed measures: **78/78**
- exact live KPI reconciliation: **34/34 PASS**
- all-measure live smoke suite: **78/78 PASS**
- Power BI semantic model connected successfully through the local Analysis Services endpoint
- exact proof: `docs/data-engineering/stage6-powerbi-runtime-proof.csv`
- smoke proof: `docs/data-engineering/stage6-measure-smoke-proof.csv`

The exact runtime suite reconciles sales, cost, profit, orders, customer/reseller counts, channel totals, role-playing due/ship dates, time intelligence, promotion logic, and latest-snapshot inventory KPIs against the SQL benchmark.

The smoke suite evaluates every governed Stage 6 measure. Measures that are legitimately blank in the current unfiltered context still pass when evaluation succeeds.

### Stage 6 decision

**Stage 6 — DAX KPI Layer: COMPLETE**

All repository, SQL, PBIP/TMDL, CI, Power BI model-load, exact KPI reconciliation, and all-measure runtime gates have passed.
