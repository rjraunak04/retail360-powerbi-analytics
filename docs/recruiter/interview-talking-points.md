# Retail360 — Interview Talking Points

## 30-second explanation

“Retail360 is an end-to-end retail analytics platform I built from Microsoft AdventureWorksDW data. I load and validate the source into PostgreSQL, transform it through raw, staging and analytics layers, model a Power BI star schema, centralize business logic in 78 governed DAX measures, build a 10-page analytical report, and validate the whole pipeline with Python, SQL, PowerShell and GitHub Actions. I also added role-playing dates, latest-snapshot inventory logic, RLS and runtime reconciliation between PostgreSQL and Power BI.”

## 90-second architecture walkthrough

1. Source CSVs are validated before loading.
2. PostgreSQL stores raw, staging and analytics layers.
3. Internet and Reseller sales are harmonized into one sales fact.
4. Inventory remains a separate Product × Date snapshot fact.
5. Power Query imports the analytics schema.
6. The semantic model uses conformed dimensions and 14 relationships.
7. A dedicated KPI_Measures table contains 78 explicit measures.
8. PBIR defines 10 visible analytical pages plus a hidden tooltip.
9. Territory RLS and enterprise QA are source-controlled.
10. GitHub Actions rebuilds and validates the project; Power BI Desktop runtime QA reconciles exact KPI outputs.

## Questions I can explain deeply

### Why a star schema?

Because predictable one-to-many relationships improve semantic clarity, filter behavior, DAX simplicity and report performance.

### Why not one giant table?

Sales and inventory have different grains. Flattening everything would duplicate snapshot or transaction data and make measures error-prone.

### How did you validate Total Sales?

I calculate the baseline in PostgreSQL and independently execute the DAX measure against the live Power BI semantic model. The Stage 6 runtime gate contains 34 exact KPI checks plus a 78-measure smoke suite.

### Why is Gross Margin % not AVERAGE(FactSales[Gross Margin Pct])?

Averaging line percentages weights each line equally. Business margin should be weighted by revenue: Total Gross Profit divided by Total Sales.

### How do Due Date and Ship Date work?

Order Date is active. Due Date and Ship Date relationships are inactive. Measures use USERELATIONSHIP and disable the active Order Date path when the alternate date role is required.

### Why is current inventory not SUM(FactInventory[Inventory Value])?

Inventory is a snapshot fact. Summing across dates double-counts the same stock position over time. Current Inventory Value filters to the global latest snapshot date.

### How did you handle channel differences?

Internet and Reseller are harmonized into one fact with a Channel dimension. Customer measures use Internet context; reseller measures use Reseller context. Not-applicable keys are explicitly controlled.

### What was a difficult engineering problem?

Power BI PBIP/TMDL runtime compatibility during Stage 6. I traced issues across table naming, stale local semantic-model state, Docker/PowerShell warnings and model runtime memory. I stabilized the design by keeping the already-proven Stage 5 source layer unchanged and isolating Stage 6 to the semantic/DAX layer.

### How is the project production-minded?

- layered warehouse
- defined fact grain
- parameterized sources
- least-privilege BI database role
- explicit measures
- RLS design
- source-controlled model/report metadata
- automated regression tests
- documented scope boundaries and data-quality edge cases

## Strong demo order

1. README architecture
2. Executive Overview
3. Sales & Growth
4. Product & Profitability
5. Inventory Analytics
6. Model / Data Quality
7. TMDL KPI_Measures file
8. PostgreSQL analytics SQL
9. GitHub Actions success
10. runtime proof CSV

## Numbers worth remembering

- 121,253 sales lines
- 776,286 inventory snapshots
- 31,455 orders
- 274,776 units
- 109.81M total sales
- 12.55M gross profit
- 78 governed DAX measures
- 34 exact live KPI runtime checks
- 78/78 measure smoke checks
- 10 report pages + 1 tooltip
- 62 visual containers
- 14 semantic relationships

## What I would build next

- historical exchange-rate fact and currency normalization
- incremental refresh for larger facts
- tenant-backed RLS identity assignment
- deployment pipeline / Power BI Service automation
- Fabric lakehouse or warehouse implementation if the business architecture requires it
