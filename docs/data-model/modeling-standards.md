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
