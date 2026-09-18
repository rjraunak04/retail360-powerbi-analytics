# Retail360 — Initial Fact Grain Definitions

These grain definitions are provisional and must be validated during source profiling before production modelling.

## FactSales

**Proposed grain:** one row per product sold through a store/channel on a transaction date at the source sales-record level.

Primary analytical use:

- Store sales
- Product performance
- Revenue
- Cost
- Gross profit
- Returns
- Discount analysis
- Promotion analysis

Important source measures include:

- SalesQuantity
- ReturnQuantity
- ReturnAmount
- DiscountQuantity
- DiscountAmount
- UnitCost
- UnitPrice
- TotalCost
- SalesAmount

## FactOnlineSales

**Proposed grain:** one row per online sales line / product transaction at source-record level.

Primary analytical use:

- E-commerce revenue
- Customer analytics
- Product performance
- Promotion performance
- Channel comparison

The final grain will be confirmed using key uniqueness tests during profiling.

## FactInventory

**Proposed grain:** one inventory snapshot per Date × Store × Product × Currency combination, subject to source validation.

Primary analytical use:

- On-hand inventory
- Inventory value
- On-order inventory
- Safety stock
- Days in stock
- Inventory ageing
- Stock-risk analysis

Important source measures include:

- OnHandQuantity
- OnOrderQuantity
- SafetyStockQuantity
- UnitCost
- DaysInStock
- Aging

## Modelling Rule

No DAX measure or Power BI visual will be built from a fact table until its grain, keys, duplicate behaviour and null behaviour have been validated.
