@'
# Retail360 — Project Charter

## Project Objective

Retail360 is an end-to-end retail analytics platform designed to provide business leaders with a unified view of sales, profitability, customers, products, stores, promotions and inventory performance.

The project demonstrates how raw retail data can be transformed into a governed analytics solution using PostgreSQL, SQL, Power Query, dimensional modelling, DAX and Power BI.

## Business Problem

Retail organisations generate transactional and operational data across products, customers, stores, inventory and promotions.

Retail360 will help decision makers answer questions such as:

- How are revenue and profit changing over time?
- Which products and categories generate the most value?
- Which stores or regions are underperforming?
- Are discounts improving sales while damaging margins?
- Which customer segments contribute the most revenue?
- Where do inventory risks exist?
- What factors are driving business performance?

## Primary Stakeholders

- Executive Leadership
- Sales Leadership
- Finance
- Category Management
- Store Management
- Inventory and Operations
- Business Analysts

## Analytics Domains

1. Executive Performance
2. Sales and Growth
3. Profitability
4. Product Performance
5. Customer Analytics
6. Store and Geographic Performance
7. Inventory Analytics
8. Promotion and Discount Analytics

## Technology Stack

- PostgreSQL
- SQL
- Power Query
- Power BI Desktop
- DAX
- Dimensional Modelling
- Power BI Service
- Git and GitHub

## Engineering Principles

- Define business logic before visuals
- Maintain clearly defined fact-table grain
- Prefer star-schema modelling
- Separate raw, staging and analytical layers
- Centralise reusable business logic
- Validate KPIs before report development
- Avoid unnecessary complexity
- Keep project documentation version controlled
'@ | Set-Content docs\business\project-charter.md

@'
# Retail360 — Data Modelling Standards

## Modelling Approach

Retail360 will use a dimensional star-schema architecture designed for analytical reporting and Power BI performance.

## Core Rules

1. Every fact table must have a clearly documented grain.
2. Dimension tables contain descriptive business attributes.
3. Relationships should primarily be one-to-many.
4. Filters should normally flow from dimensions to facts.
5. Many-to-many relationships require explicit justification.
6. Business KPIs should use explicit DAX measures.
7. Technical keys should be hidden from report consumers.
8. Time intelligence must use a dedicated Date dimension.
9. Source transformations must remain separate from presentation logic.
10. KPI definitions must be documented and validated before use.

## Proposed Naming Convention

### Dimension Tables

- DimDate
- DimProduct
- DimCustomer
- DimStore
- DimGeography
- DimPromotion

### Fact Tables

- FactSales
- FactInventory
- FactReturns

These tables are provisional until source-data profiling confirms the final model.

## Measure Naming

Measures should use readable business terminology such as:

- Total Sales
- Gross Profit
- Gross Margin %
- Sales YoY %
- Average Order Value
- Units Sold
'@ | Set-Content docs\data-model\modeling-standards.md