# Retail360 — Data Source Strategy

## Selected Source

Retail360 will use the Microsoft Contoso retail data warehouse as the primary learning and portfolio dataset.

Contoso is a fictional retail business dataset published by Microsoft for BI and data warehouse scenarios. It contains a realistic multi-domain retail structure covering sales, online sales, customers, products, stores, geography, promotions, inventory, channels and finance-related entities.

## Why This Dataset

The dataset supports a stronger portfolio project than a single flat retail CSV because it allows Retail360 to demonstrate:

- Multiple business domains
- Multiple fact tables
- Shared conformed dimensions
- Store and online sales analysis
- Customer analytics
- Product/category analytics
- Promotion effectiveness
- Inventory analytics
- Geographic analysis
- Dimensional modelling
- SQL transformation layers
- Power BI semantic modelling

## Retail360 Scope

Retail360 will initially use only the tables required for the core analytical product.

### Core dimensions

- DimDate
- DimProduct
- DimProductSubcategory
- DimProductCategory
- DimCustomer
- DimStore
- DimGeography
- DimPromotion
- DimChannel
- DimCurrency

### Core facts

- FactSales
- FactOnlineSales
- FactInventory

Additional source tables will only be introduced when they answer a defined business requirement.

## Data Engineering Approach

The Microsoft source model will not be copied directly into Power BI.

Retail360 will use the following flow:

Source retail data
→ PostgreSQL raw layer
→ PostgreSQL staging layer
→ PostgreSQL analytics layer
→ Power Query
→ Power BI semantic model
→ DAX
→ Business reports

## Portfolio Principle

The goal is not to reproduce Microsoft's existing demo dashboard.

The goal is to use the source data to design and implement an independent Retail360 analytics solution with documented business logic, quality checks, dimensional modelling, Power BI measures and executive reporting.
