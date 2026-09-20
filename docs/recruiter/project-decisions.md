# Retail360 — Project Decisions & Trade-offs

This document explains the choices that matter most in a technical interview.

## 1. AdventureWorksDW instead of a fabricated retail dataset

The project uses Microsoft AdventureWorksDW sample data so the source is reproducible and independently recognizable. The engineering value comes from the warehouse, modelling, KPI governance, QA and Power BI implementation rather than from inventing synthetic business data.

## 2. PostgreSQL layered warehouse

The database is separated into:

- `raw` — faithful typed landing
- `staging` — cleanup, harmonization and reusable transformations
- `analytics` — stable reporting star schema
- `audit` — reconciliation / pipeline evidence

This keeps ingestion concerns separate from reporting logic.

## 3. One harmonized sales fact

Internet and Reseller transactions are combined into one analytical `FactSales` with a conformed Channel dimension.

Why:

- common KPI logic
- simpler executive reporting
- consistent time/product/territory analysis

Risk handled:

Internet and Reseller order identifiers can overlap, so Distinct Orders uses **Channel + Sales Order Number** instead of Sales Order Number alone.

## 4. Inventory remains a snapshot fact

Inventory has a different grain from sales: Product × Date snapshot.

Headline inventory measures use the latest available snapshot. Summing inventory value across all historical snapshots would overstate current stock.

## 5. Gross Margin % is weighted

Correct:

`Gross Profit / Total Sales`

Incorrect:

average of row-level margin percentages.

The weighted approach is implemented as a governed DAX measure.

## 6. Role-playing dates stay in one DimDate

FactSales has Order, Due and Ship date keys.

- Order Date relationship is active.
- Due Date is inactive.
- Ship Date is inactive.

Due/Ship measures activate the appropriate relationship through `USERELATIONSHIP` and explicitly remove the active Order Date relationship where required.

## 7. Unknown members are explicit

Key-0 members are used for dimensions where Unknown / Not Applicable is meaningful.

The Date key-0 row was removed because no fact row used it and a blank date breaks marked-date-table requirements.

## 8. No false currency claim

Sales facts contain CurrencyKey, but historical exchange-rate data is not part of the current project.

Therefore consolidated sales/profit measures deliberately use neutral number formats instead of being labeled USD.

## 9. Promotion analysis is descriptive, not causal

The project reports discounted sales, discount amount and related measures.

It does **not** claim that a promotion caused sales lift because there is no experiment, control group or causal identification strategy.

## 10. Negative historical inventory is preserved

A real source-level edge case exists: 3,319 historical inventory snapshots contain negative units balance and correspondingly negative inventory value.

The project validates the arithmetic and preserves the data rather than silently clipping or rewriting it.

## 11. PBIP/TMDL/PBIR is canonical

The source-controlled project format is the canonical implementation because it enables:

- meaningful Git diffs
- model/report metadata review
- automated validation
- branch-based collaboration

PBIX is treated as an optional distribution artifact.

## 12. RLS inventory is fail-closed

Territory RLS filters sales through Sales Territory.

FactInventory has no territory grain, so the demonstration territory roles deny inventory rows rather than pretending inventory can be safely allocated to a territory.

## 13. Stage 6 uses a static KPI_Measures host

The measure host is a one-row static M table named `KPI_Measures`.

The name avoids a Power BI compatibility issue with `Measures`, and the static host avoids calculated-table dependency behavior while keeping measures organized.

## 14. CI validates structure, Desktop validates runtime

GitHub Actions can fully rebuild PostgreSQL and validate source-controlled Power BI metadata.

Power BI Desktop-specific runtime evidence is captured separately through the local Analysis Services endpoint. This avoids pretending Linux CI can execute Power BI Desktop.
