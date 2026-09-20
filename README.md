<div align="center">

# 🛒 Retail360 — Enterprise Retail Analytics Platform

**End-to-end retail BI engineering with PostgreSQL, Power Query, dimensional modeling, governed DAX, PBIP/TMDL and automated QA.**

[![Power BI](https://img.shields.io/badge/Power%20BI-PBIP%20%7C%20TMDL-F2C811?logo=powerbi&logoColor=black)](powerbi/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](sql/)
[![DAX](https://img.shields.io/badge/DAX-78%20Governed%20Measures-2563EB)](docs/powerbi/kpi-dictionary.md)
[![Power Query](https://img.shields.io/badge/Power%20Query-M-00B294)](power-query/)
[![Python](https://img.shields.io/badge/Python-QA%20%26%20Automation-3776AB?logo=python&logoColor=white)](scripts/)
[![Docker](https://img.shields.io/badge/Docker-Local%20Warehouse-2496ED?logo=docker&logoColor=white)](compose.yml)
[![CI](https://github.com/rjraunak04/retail360-powerbi-analytics/actions/workflows/postgres-stage2-ci.yml/badge.svg?branch=develop)](https://github.com/rjraunak04/retail360-powerbi-analytics/actions/workflows/postgres-stage2-ci.yml)

**Sales • Profitability • Customers • Products • Resellers • Promotions • Territory • Inventory**

[Architecture](docs/architecture/retail360-architecture.md) •
[Star Schema](docs/architecture/star-schema.md) •
[KPI Dictionary](docs/powerbi/kpi-dictionary.md) •
[Dashboard Gallery](docs/screenshots/README.md) •
[Setup](docs/project/setup.md)

</div>

---

Retail360 is a source-controlled analytics platform built on **Microsoft AdventureWorksDW**. It takes raw CSV extracts through a reproducible **PostgreSQL warehouse → staging layer → analytics star schema → Power BI semantic model → governed DAX layer → report**, with automated validation at each stage.

### ⚡ At a glance

| Area | Implementation |
|---|---|
| 🗄️ Warehouse | PostgreSQL 16 with `raw`, `staging`, `analytics`, `audit` schemas |
| ⭐ Data model | Governed star schema with Sales + Inventory facts |
| 🧮 Semantic layer | PBIP / TMDL / PBIR source-controlled Power BI model |
| 📊 DAX | 78 explicit governed measures |
| ✅ QA | SQL reconciliation, semantic-model checks and runtime DAX tests |
| 🐳 Local setup | Docker-based PostgreSQL environment |
| 🔁 CI | GitHub Actions regression validation |

![Retail360 Executive Overview](docs/screenshots/01-executive-overview.png)

## What the project covers

The model supports analysis across sales, profitability, products, customers, resellers, promotions, territories and inventory.

Key implementation points:

- PostgreSQL 16 warehouse with `raw`, `staging`, `analytics` and `audit` schemas
- harmonized Internet + Reseller sales fact with 121,253 sales lines
- inventory snapshot fact with 776,286 product/date rows
- PBIP/TMDL/PBIR source control for the Power BI model and report
- 78 explicit governed measures in `KPI_Measures`
- 34/34 exact KPI runtime checks and 78/78 measure smoke checks
- 10 analytical pages + 1 hidden report-page tooltip
- territory-based demonstration RLS
- Docker-based local PostgreSQL and GitHub Actions regression checks

## Business questions

Retail360 is designed to answer questions such as:

- How are sales, units, orders and gross profit changing over time?
- Which products and categories contribute most to revenue and margin?
- How do Internet and Reseller channels compare?
- Which customers and resellers generate the most value?
- Which territories contribute the most sales?
- How much revenue is associated with discounts?
- What is the latest inventory position?
- Which products are below safety-stock thresholds?

## Architecture

```mermaid
flowchart LR
    A[AdventureWorksDW CSV] --> B[Source validation]
    B --> C[(PostgreSQL raw)]
    C --> D[(PostgreSQL staging)]
    D --> E[(PostgreSQL analytics)]
    E --> F[Power Query Import]
    F --> G[PBIP / TMDL Semantic Model]
    G --> H[KPI_Measures]
    H --> I[Power BI Report]
    G --> J[RLS + QA]

    K[Python + SQL validation] --> C
    K --> D
    K --> E
    L[GitHub Actions] --> K
    L --> G
    L --> I
```

More detail:
- [Architecture](docs/architecture/retail360-architecture.md)
- [Star schema](docs/architecture/star-schema.md)
- [Architecture decisions](docs/project/architecture-decisions.md)

## Verified KPI baseline

The following values are reconciled between the PostgreSQL analytics layer and the Power BI semantic model.

| KPI | Verified value |
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
| Current Inventory Value | 23,603,975.5700 |
| Current Inventory Units | 258,981 |
| Products Below Safety Stock | 543 |

## Power BI model

The semantic model uses a governed star schema with:

- `FactSales` at sales-order-line grain
- `FactInventory` at product × date snapshot grain
- conformed Date, Product, Customer, Reseller, Employee, Geography, Sales Territory, Promotion, Currency and Channel dimensions
- active Order Date plus inactive Due Date and Ship Date relationships
- explicit measures only; implicit measures are discouraged

The DAX layer includes sales, profitability, time intelligence, role-playing dates, customer/reseller, product, channel, promotion and inventory measures.

Important modelling rules:

- Gross Margin % = Gross Profit / Total Sales
- distinct orders use Channel + Sales Order Number
- Due Date and Ship Date measures use `USERELATIONSHIP`
- headline inventory KPIs use the latest snapshot rather than summing historical snapshots
- consolidated monetary values remain currency-symbol neutral because exchange-rate history is outside the project scope

[KPI dictionary](docs/powerbi/kpi-dictionary.md)

## Report

The source-controlled report contains:

1. Executive Overview
2. Sales & Growth
3. Product & Profitability
4. Customer Analytics
5. Channel / Reseller Analytics
6. Geography & Territory
7. Promotion Analysis
8. Inventory Analytics
9. Drill-through Detail
10. Model / Data Quality
11. Product Tooltip — hidden report-page tooltip

The report uses a consistent 1280×720 layout, governed measures, native visuals, drillthrough and report-page tooltips.

[Dashboard gallery](docs/screenshots/README.md)

## Validation

This repository treats validation as part of the implementation rather than as a separate manual step.

| Layer | Validation |
|---|---|
| Source | row shape, parser checks, PK/FK integrity |
| PostgreSQL raw | 14-table reconciliation |
| Staging | type and business-rule checks |
| Analytics | fact grain, FKs and metric preservation |
| Semantic model | tables, relationships, parameters and role dates |
| DAX | SQL benchmark reconciliation + runtime checks |
| Report | page, visual, binding, drillthrough and tooltip contracts |
| Security | RLS definitions and regional runtime baselines |
| Deployment | packaging, manifest and integrity checks |

Canonical Power BI runtime evidence:
- [Stage 6 exact KPI proof](docs/data-engineering/stage6-powerbi-runtime-proof.csv)
- [Stage 6 measure smoke proof](docs/data-engineering/stage6-measure-smoke-proof.csv)
- [Stage 8 enterprise QA](docs/data-engineering/stage8-validation-summary.md)

## Repository structure

```text
retail360-powerbi-analytics/
├── data/                    # local source-data workflow
├── dax/                     # DAX QA queries
├── docs/
│   ├── architecture/        # architecture and star schema
│   ├── business/            # business context
│   ├── data-engineering/    # validation evidence
│   ├── data-model/          # semantic-model documentation
│   ├── deployment/          # deployment and refresh notes
│   ├── powerbi/             # KPI and report documentation
│   ├── project/             # setup and design decisions
│   ├── qa/                  # QA notes and packaging checks
│   ├── screenshots/         # rendered report gallery
│   └── sql/                 # concise analysis examples
├── power-query/             # M queries
├── powerbi/                 # PBIP / PBIR / TMDL source
├── scripts/                 # build and validation automation
├── sql/                     # warehouse, staging and analytics SQL
├── compose.yml              # local PostgreSQL
└── .github/workflows/       # CI
```

## Quick start

Prerequisites: Git, Python 3.11+, Docker Desktop and Power BI Desktop.

```powershell
git clone https://github.com/rjraunak04/retail360-powerbi-analytics.git
cd retail360-powerbi-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d postgres
Start-Process .\powerbi\Retail360.pbip
```

For the full local rebuild and validation sequence, see [Setup](docs/project/setup.md).

## Selected design decisions

A few choices are deliberate and documented:

- Internet and Reseller transactions share one harmonized sales fact.
- Inventory stays a separate snapshot fact because its grain differs from sales.
- key-0 unknown members are used only where they are meaningful.
- negative historical inventory rows are preserved and validated rather than silently rewritten.
- promotion analysis is descriptive; the project does not claim causal lift.
- currency totals are not labeled as USD without an exchange-rate fact.
- PBIP/TMDL/PBIR is the canonical source-controlled format.

[Design decisions and trade-offs](docs/project/architecture-decisions.md)

## SQL examples

A short set of queries showing the core business logic is available in [Business analysis SQL examples](docs/sql/business-analysis-examples.md).

## Deployment

The canonical distributable artifact is the source-controlled `powerbi/Retail360.pbip` project. A versioned local release package can be generated with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package_stage10_release.ps1
```

Power BI Service publication is intentionally documented as environment-specific rather than claimed without tenant evidence.

[Deployment notes](docs/deployment/stage10-deployment-summary.md)

## Scope

Implemented:
- PostgreSQL warehouse and dimensional model
- Power BI semantic model and report
- governed DAX KPI layer
- RLS demonstration roles
- automated validation
- reproducible local packaging

Not claimed:
- causal promotion lift
- historical FX conversion without rate history
- production Fabric / ADF / Synapse implementation
- tenant-level Power BI Service deployment without environment evidence

## Status

The portfolio/fallback deployment path is complete and CI-validated. Power BI Service publication remains an optional environment-specific deployment step.

[Project roadmap](docs/roadmap/end-to-end-build-plan.md)
