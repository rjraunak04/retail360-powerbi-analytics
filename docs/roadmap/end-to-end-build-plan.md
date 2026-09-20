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

Exit gate:
- zero malformed rows caused by parser logic
- zero duplicate/null grain keys
- referential-integrity checks understood and documented

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


Target semantic entities:
- DimDate
- DimProduct
- DimCustomer
- DimReseller
- DimGeography / DimTerritory
- DimPromotion
- DimCurrency
- DimEmployee (only where analytically needed)
- FactSales (harmonised Internet + Reseller)
- FactInventory

Exit gate:
- one-to-many relationships
- explicit fact grains
- conformed dimensions
- no accidental many-to-many relationships

## Stage 5 — Power BI Semantic Model
Status: COMPLETE


Deliverables:
- PostgreSQL connection
- Power Query staging
- star-schema relationships
- dedicated measure table
- hidden technical keys
- correct data categories and formatting
- Date table marked properly

## Stage 6 — DAX KPI Layer
Status: COMPLETE


Core KPI groups:
- Sales: Total Sales, Units, Orders, ASP
- Profitability: Total Cost, Gross Profit, Gross Margin %
- Growth: MTD/QTD/YTD, YoY, YoY %
- Customer: Customers, Revenue per Customer, Repeat/segment metrics where valid
- Product: Category contribution, product ranking
- Channel: Internet vs Reseller
- Promotion: promoted sales, discount impact
- Inventory: Units Balance, Inventory Value, inventory movement

## Stage 7 — Recruiter-Grade Report UX
Status: COMPLETE

Pages:
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

UX:
- consistent grid and spacing
- KPI cards
- variance indicators
- dynamic titles
- field parameters where useful
- report-page tooltips
- drillthrough
- bookmarks only where they improve navigation

## Stage 8 — Enterprise Features and QA
Status: COMPLETE


Deliverables:
- territory-based RLS roles with fail-closed inventory behavior
- Performance Analyzer / report-structure review
- DAX optimisation contract
- relationship and security-direction QA
- KPI reconciliation against PostgreSQL
- SQL edge-case testing
- refresh/deployment notes
- PBIP/PBIX source-control strategy
- one-command Stage 8 enterprise runtime gate

## Stage 9 — GitHub and Recruiter Packaging

Deliverables:
- final README
- architecture diagram
- star-schema diagram
- dashboard screenshots
- KPI dictionary
- SQL examples
- project decisions / trade-offs
- setup instructions
- interview talking points
- CV bullets
- LinkedIn/GitHub project description

## Stage 10 — Deployment

Preferred:
- publish to Power BI Service where account capabilities allow
- configure credentials/refresh where feasible
- document workspace/report deployment

Fallback:
- polished PBIX/PBIP in repository-compatible structure
- screenshots and walkthrough
- reproducible local setup

## Build Rule

No stage is considered complete only because a file exists. Each stage must pass an explicit validation gate before the next layer is treated as production-ready.
