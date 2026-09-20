# Retail360 — End-to-End Build Plan

## Goal

Complete Retail360 as a recruiter-ready end-to-end retail analytics portfolio project with reproducible source acquisition, data-quality validation, PostgreSQL data engineering, dimensional modelling, Power BI semantic modelling, DAX, dashboard UX, QA, documentation and deployment evidence.

## Stage 0 — Project Foundation
Status: COMPLETE

Deliverables:
- Git/GitHub workflow
- project charter
- modelling standards
- repository structure
- source-control conventions

## Stage 1 — Data Foundation
Status: COMPLETE

Deliverables:
- official Microsoft AdventureWorksDW source download
- 11 dimensions + 3 fact tables
- raw profiling
- source data dictionary
- primary/grain-key validation
- foreign-key validation
- documented fact grains

## Stage 2 — PostgreSQL Warehouse Foundation
Status: COMPLETE

Deliverables:
- retail360 database
- raw, staging, analytics schemas
- typed raw landing tables
- reproducible ingestion script
- row-count reconciliation
- SQL quality checks

## Stage 3 — Staging and Business Transformation
Status: COMPLETE

Deliverables:
- cleaned and typed staging views/tables
- business-friendly names
- derived gross profit and margin fields
- channel standardisation
- customer/product/geography enrichment
- date handling
- null/unknown-member policy

## Stage 4 — Analytics Star Schema
Status: COMPLETE

Deliverables:
- conformed dimensions
- harmonised FactSales
- FactInventory snapshot fact
- one-to-many relationships
- explicit fact grains
- controlled unknown-member policy

## Stage 5 — Power BI Semantic Model
Status: COMPLETE

Deliverables:
- PostgreSQL connection
- Power Query import layer
- star-schema relationships
- hidden technical keys
- Date table
- PBIP/TMDL/PBIR source control

## Stage 6 — DAX KPI Layer
Status: COMPLETE

Deliverables:
- 78 governed explicit measures
- sales/profitability/growth KPIs
- customer/reseller/product/channel KPIs
- role-playing date measures
- latest-snapshot inventory logic
- exact KPI runtime proof and all-measure smoke proof

## Stage 7 — Recruiter-Grade Report UX
Status: COMPLETE

Deliverables:
- 10 visible analytical pages
- 1 hidden report-page tooltip
- consistent grid, cards, trends and comparison visuals
- drillthrough and tooltip behaviour
- CI-validated PBIR structure

## Stage 8 — Enterprise Features and QA
Status: COMPLETE

Deliverables:
- territory-based demonstration RLS
- relationship/security-direction QA
- DAX optimisation contract
- SQL edge-case testing
- refresh/deployment notes
- PBIP/PBIX strategy
- enterprise runtime QA

## Stage 9 — Repository & Portfolio Packaging
Status: COMPLETE

Deliverables:
- final README
- architecture and star-schema diagrams
- 10 dashboard screenshots
- KPI dictionary
- business-analysis SQL examples
- architecture decisions / trade-offs
- setup instructions
- repository packaging validation

## Stage 10 — Deployment
Status: COMPLETE — PORTFOLIO/FALLBACK DEPLOYMENT

Completed:
- canonical source-controlled PBIP distribution artifact
- versioned release manifest
- one-command release packaging helper
- SHA-256 integrity manifest
- reproducible local deployment/demo path
- Power BI Service publication checklist
- gateway/cloud PostgreSQL refresh guidance
- generated release output excluded from source control
- CI deployment-contract validation

Power BI Service publication is environment-dependent and is not claimed until an authenticated tenant/workspace, connection or gateway, refresh, and RLS membership are configured and evidenced.

Preferred environment path:
- publish to Power BI Service when account capabilities allow
- configure credentials/connection or gateway
- validate on-demand and scheduled refresh
- assign/test RLS membership

Completed fallback path:
- polished PBIP/PBIR/TMDL repository artifact
- screenshots and recruiter walkthrough
- reproducible local setup
- versioned ZIP package generated on demand

Exit gate:
- `python scripts/validate_stage10_deployment.py` passes
- `scripts/package_stage10_release.ps1` parses successfully
- Stage 10 CI is green
- no credentials or machine-local caches are distributed

## Build Rule

No stage is considered complete only because a file exists. Each stage must pass an explicit validation gate before it is treated as production-ready.
