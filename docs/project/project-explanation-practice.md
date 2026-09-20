# Retail360 — Project Explanation & Interview Practice

## 30-second recruiter pitch

Retail360 is an end-to-end retail analytics platform built on Microsoft AdventureWorksDW. I designed a reproducible pipeline from raw CSV data into PostgreSQL, created cleaned staging and analytics star-schema layers, connected the model to Power BI through parameterized Power Query, built a source-controlled PBIP/TMDL semantic model with 78 governed DAX measures, and created 10 analytical report pages plus drillthrough and tooltip experiences. I also added automated SQL, semantic-model, DAX, RLS, report-structure and deployment validation through Python, PowerShell and GitHub Actions.

## 2-minute interview walkthrough

I started with the business problem: retail leadership needs one governed view of revenue, profitability, customers, products, channels, territories, promotions and inventory.

The source is Microsoft AdventureWorksDW. I built a reproducible ingestion process that lands 14 source files into PostgreSQL. The warehouse has raw, staging, analytics and audit schemas. Staging handles typing, standardisation and derived business fields. The analytics layer uses a star schema with a harmonised sales fact at sales-order-line grain and a separate inventory snapshot fact at product-by-date grain.

In Power BI, I kept the semantic model source-controlled using PBIP, TMDL and PBIR. The model uses conformed dimensions, one-to-many single-direction relationships and role-playing dates. Order Date is active while Due Date and Ship Date are inactive and activated only in explicit measures.

The KPI layer contains 78 governed measures. Important examples are Total Sales, Gross Profit, weighted Gross Margin %, distinct business orders, Internet versus Reseller sales, customer/reseller KPIs, time intelligence and latest-snapshot inventory metrics. I deliberately avoid averaging row-level margin percentages and I do not label consolidated revenue as USD because the project does not contain a historical exchange-rate fact.

The report contains 10 visible analytical pages and one hidden product tooltip page. It includes executive, sales, product, customer, reseller/channel, territory, promotion and inventory analysis plus drillthrough and model/data-quality pages.

The project is also engineered for reproducibility. SQL baselines are reconciled against Power BI, Stage 6 has 34 exact runtime KPI checks and a 78-measure smoke suite, Stage 8 adds RLS and enterprise QA, and GitHub Actions rebuilds and validates the project. A versioned release package with checksums can be generated for portfolio deployment.

## Architecture to explain on a whiteboard

```text
AdventureWorksDW CSV
        |
        v
Source integrity validation
        |
        v
PostgreSQL raw
        |
        v
PostgreSQL staging
        |
        v
PostgreSQL analytics star schema
        |
        v
Power Query Import
        |
        v
PBIP / TMDL semantic model
        |
        v
KPI_Measures (78 governed DAX measures)
        |
        v
PBIR report (10 pages + tooltip)
        |
        v
QA / RLS / packaging / deployment
```

## Numbers worth remembering

| Metric | Verified value |
|---|---:|
| Source rows | 922,106 |
| FactSales rows | 121,253 |
| FactInventory rows | 776,286 |
| Distinct orders | 31,455 |
| Units sold | 274,776 |
| Total Sales | 109,809,274.2030 |
| Total Product Cost | 97,257,907.9547 |
| Gross Profit | 12,551,366.2483 |
| Customers | 18,484 |
| Repeat Customers | 6,865 |
| Resellers | 635 |
| Products Sold | 350 |
| Current Inventory Value | 23,603,975.5700 |
| Current Inventory Units | 258,981 |
| Governed DAX measures | 78 |
| Exact Power BI runtime checks | 34 |
| Report pages | 10 visible + 1 tooltip |

## Key design decisions

### Why one FactSales instead of separate Internet and Reseller facts?

Both sources represent sales-order-line events and can be harmonised to one grain. A Channel dimension preserves the business distinction while simplifying cross-channel analysis.

### Why is inventory separate from sales?

Inventory is a snapshot fact at Product × Date grain. Combining it with transactional sales would create grain ambiguity and incorrect aggregation.

### Why is Gross Margin % not averaged?

Margin is a ratio. The governed calculation is:

`Gross Margin % = Gross Profit / Total Sales`

Averaging row-level percentages would give each row equal weight and produce the wrong business result.

### Why are Due Date and Ship Date relationships inactive?

A date dimension can have only one active filtering path to the same fact in this design. Order Date is the default active relationship. Due/Ship measures use `USERELATIONSHIP` and explicitly disable the Order Date path where required.

### Why are inventory headline KPIs based on the latest snapshot?

Summing inventory value across historical snapshots double-counts stock over time. Current Inventory Value and Current Inventory Units evaluate only the latest available snapshot.

### Why no currency symbol on consolidated monetary measures?

The facts contain currency keys but this project does not include historical exchange-rate data. The totals are therefore kept currency-symbol neutral rather than making an unsupported USD claim.

### Why preserve negative historical inventory balances?

They are present in the source. The project validates the arithmetic and documents the edge case rather than silently changing source behaviour.

## Difficult problems I solved

1. **Data ingestion reliability:** source files have unconventional delimiters, blank terminal fields and some NUL bytes. The ingestion pipeline normalises these cases and validates row counts and keys.
2. **Semantic-model reproducibility:** the Power BI model is source-controlled with PBIP/TMDL rather than existing only as a binary PBIX.
3. **Power BI runtime compatibility:** Stage 6 exposed stale-model, reserved-name and memory/runtime issues. The stable design kept the already-proven Stage 5 source partitions and isolated Stage 6 changes to the governed KPI layer.
4. **Inventory semantics:** I separated additive historical snapshot metrics from current-state KPIs.
5. **Validation:** PostgreSQL baselines, DAX runtime checks and report-structure validation prevent visually plausible but numerically incorrect dashboards.

## Common interview questions

### What is the grain of FactSales?

One harmonised sales-order line. Internet and Reseller rows share the same fact and are differentiated by Channel Key.

### What is the grain of FactInventory?

One Product × Date inventory snapshot.

### What is a conformed dimension here?

A dimension such as Product or Date that consistently filters multiple relevant facts. Product and Date are shared by Sales and Inventory.

### How did you calculate distinct orders across two channels?

I count unique combinations of Channel Key and Sales Order Number. This prevents accidental collisions if the same order-number text exists in both channels.

### How did you validate Power BI against SQL?

I created SQL benchmarks in PostgreSQL and equivalent DAX runtime checks. The exact Stage 6 suite compares 34 important KPI identities and expected values, while the smoke suite evaluates all 78 measures.

### How did you implement RLS?

Stage 8 contains three demonstration territory roles: North America, Europe and Pacific. The filter is applied at the Sales Territory dimension. Inventory is denied in these demo roles because inventory has no territory grain; allowing it would imply a security relationship that does not exist.

### Why did you use Import mode?

The dataset size is appropriate for Import mode, and it provides responsive report interactions. The project keeps refresh configuration separate from model logic and documents Service/gateway options.

### What would you change for production scale?

I would use managed/cloud PostgreSQL or a governed warehouse, incremental refresh for large facts, environment-specific deployment pipelines, formal identity/role management, monitoring, and possibly Fabric components only when the production architecture actually requires them.

### Did you use Fabric, ADF or Synapse?

No. I do not claim tools that are not implemented. The project is PostgreSQL + Power BI + Python/SQL automation, with deployment guidance for Power BI Service.

## Five-minute demo sequence

1. **Executive Overview** — explain headline Sales, Profit, Margin and Orders.
2. **Sales & Growth** — show time trend and channel mix.
3. **Product & Profitability** — identify leading categories/products and explain weighted margin.
4. **Customer / Reseller** — explain the two business channels and entity metrics.
5. **Inventory Analytics** — emphasise latest-snapshot logic and safety-stock risk.
6. **Drill-through Detail** — demonstrate detail navigation without duplicating business logic.
7. **Model / Data Quality** — show that validation is part of the product, not an afterthought.
8. Finish with the GitHub repository: SQL, TMDL, DAX QA, CI and deployment docs.

## What to say if a recruiter asks “What did you personally do?”

I designed the data flow, model grain, PostgreSQL warehouse layers, star schema, Power Query connection pattern, semantic relationships, DAX KPI definitions, Power BI report structure, validation approach, RLS demonstration, documentation and release packaging. The project is intentionally reproducible so each layer can be inspected and rebuilt rather than existing only as screenshots.

## What not to overclaim

Do not claim:

- promotion analysis proves causal uplift
- consolidated monetary totals are converted to USD
- Power BI Service has been published unless tenant evidence actually exists
- Fabric/ADF/Synapse are implemented
- inventory has territory-level RLS when no territory relationship exists

## Resume bullets

- Built **Retail360**, an end-to-end retail BI platform using PostgreSQL, Power Query and Power BI, modelling **121K+ sales lines** and **776K+ inventory snapshots** in a governed star schema.
- Developed **78 explicit DAX measures** for sales, profitability, growth, customer/reseller, product, promotion and latest-snapshot inventory analytics; reconciled critical KPIs with **34/34 live runtime checks**.
- Source-controlled the Power BI solution with **PBIP/TMDL/PBIR**, added territory-based RLS demonstrations, automated QA with Python/PowerShell and GitHub Actions, and packaged a reproducible portfolio release.

## One-line GitHub / LinkedIn description

Retail360 is a source-controlled enterprise retail analytics project that moves AdventureWorksDW data through PostgreSQL into a governed Power BI semantic model with 78 DAX measures, 10 analytical pages, automated QA, RLS and reproducible deployment packaging.

## Final practice checklist

Before an interview, be able to explain without notes:

- FactSales and FactInventory grain
- why the model uses two facts
- active vs inactive date relationships
- weighted Gross Margin %
- distinct-order logic
- latest inventory snapshot logic
- one SQL-to-DAX reconciliation example
- one RLS design decision
- one runtime/debugging problem and how you fixed it
- what is intentionally outside project scope
