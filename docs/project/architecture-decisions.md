# Architecture Decisions & Trade-offs

This document records the modelling and engineering choices that shape Retail360.

## Source data

The project uses Microsoft AdventureWorksDW sample data so the source is reproducible and independently recognizable. The engineering work is in the warehouse, dimensional model, KPI layer, QA and Power BI implementation.

## Layered PostgreSQL warehouse

The database is separated into:

- `raw` — faithful typed landing
- `staging` — cleanup, harmonization and reusable transformations
- `analytics` — stable reporting star schema
- `audit` — reconciliation and validation evidence

This keeps ingestion concerns separate from reporting logic.

## One harmonized sales fact

Internet and Reseller transactions are combined into one analytical `FactSales` with a conformed Channel dimension. This keeps KPI logic consistent across channels.

Internet and Reseller order numbers can overlap, so distinct orders use **Channel + Sales Order Number** rather than Sales Order Number alone.

## Inventory remains a snapshot fact

Inventory has a different grain from sales: Product × Date snapshot.

Headline inventory measures use the latest available snapshot. Summing inventory value across historical snapshots would overstate current stock.

## Weighted gross margin

Gross Margin % is defined as:

`Gross Profit / Total Sales`

The model deliberately does not average row-level margin percentages.

## Role-playing dates

`FactSales` contains Order, Due and Ship date keys.

- Order Date is active.
- Due Date is inactive.
- Ship Date is inactive.

Measures for Due/Ship dates activate the appropriate relationship with `USERELATIONSHIP`.

## Unknown members

Key-0 members are used where Unknown / Not Applicable is meaningful.

The Date key-0 row is intentionally absent because no fact row uses it and a blank date would break Date-table requirements.

## Currency scope

The sales facts contain CurrencyKey, but historical exchange-rate data is not part of the project. Consolidated monetary measures therefore use neutral number formats instead of being labeled as USD.

## Promotion scope

Promotion analysis is descriptive. The project reports discounted sales and discount measures but does not claim that a promotion caused sales lift.

## Negative historical inventory

The source contains historical inventory snapshots with negative units balance. The project validates and preserves those rows rather than silently clipping them.

## PBIP/TMDL/PBIR as the canonical format

The source-controlled Power BI project format is canonical because it supports meaningful Git diffs, model/report metadata review and automated validation.

PBIX is treated as an optional distribution format.

## RLS inventory behavior

Territory roles filter sales through Sales Territory. Inventory has no territory grain, so the demonstration roles fail closed for inventory rather than pretending inventory can be allocated safely to a territory.

## KPI measure host

The 78 governed measures live in a one-row static M table named `KPI_Measures`. Keeping the host static avoids calculated-table dependency behavior while preserving a clear measure organization point.

## CI versus Desktop runtime

GitHub Actions rebuilds PostgreSQL and validates source-controlled Power BI metadata. Desktop-specific runtime evidence is captured separately through the local Analysis Services endpoint rather than pretending Linux CI can execute Power BI Desktop.
