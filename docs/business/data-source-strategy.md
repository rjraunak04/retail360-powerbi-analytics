# Retail360 — Data Source Strategy

## Selected Source

Retail360 uses the official Microsoft AdventureWorks Data Warehouse CSV source files from the microsoft/sql-server-samples repository.

AdventureWorks represents a multi-channel retail business and provides a realistic dimensional warehouse structure for portfolio-grade analytics. The source includes customer, employee, product, geography, promotion, reseller, sales-territory, internet-sales, reseller-sales and product-inventory data.

## Why This Dataset

This source is preferred for Retail360 because it is:

- Published and maintained in Microsoft's official SQL Server samples repository
- Directly downloadable as individual source CSV files
- Suitable for PostgreSQL ingestion without requiring a SQL Server backup restore
- Multi-table and relational rather than a single flat dashboard CSV
- Rich enough to demonstrate customer, product, geography, promotion, channel, profitability and inventory analytics
- Appropriate for dimensional modelling, data-quality testing, SQL transformation and Power BI semantic modelling

## Retail360 Scope

### Core dimensions

- DimDate
- DimProduct
- DimProductSubcategory
- DimProductCategory
- DimCustomer
- DimEmployee
- DimGeography
- DimPromotion
- DimCurrency
- DimSalesTerritory
- DimReseller

### Core facts

- FactInternetSales
- FactResellerSales
- FactProductInventory

### Optional analytical extensions

- DimSalesReason
- FactInternetSalesReason

Optional tables will only be introduced when they answer a documented business requirement.

## Analytical Domains

- Executive retail performance
- Revenue and profitability
- Product and category performance
- Customer analytics
- Geography and sales-territory performance
- Internet versus reseller channel analysis
- Promotion and discount analysis
- Product inventory analysis

## Data Engineering Approach

Retail360 will not connect the Microsoft source files directly to final report visuals.

Microsoft source CSV files → local raw landing zone → PostgreSQL raw schema → PostgreSQL staging schema → PostgreSQL analytics/star-schema layer → Power Query → Power BI semantic model → DAX → business reports

## Portfolio Principle

Retail360 is an independent analytics implementation. The Microsoft source data is used as the input dataset, while the ingestion process, PostgreSQL layers, business rules, quality checks, semantic model, DAX measures, report design and documentation are built specifically for this project.
