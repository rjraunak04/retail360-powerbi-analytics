# Retail360 — Initial Fact Grain Definitions

These grain definitions are provisional until they are validated against the downloaded source files.

## FactInternetSales

**Proposed grain:** one row per internet sales order line, identified by SalesOrderNumber × SalesOrderLineNumber.

Primary analytical use:
- E-commerce revenue
- Customer purchasing behaviour
- Product and category performance
- Promotion effectiveness
- Discount analysis
- Gross profit analysis
- Geographic and territory analysis

Important source measures include:
- OrderQuantity
- UnitPrice
- ExtendedAmount
- UnitPriceDiscountPct
- DiscountAmount
- ProductStandardCost
- TotalProductCost
- SalesAmount
- TaxAmt
- Freight

## FactResellerSales

**Proposed grain:** one row per reseller sales order line, identified by SalesOrderNumber × SalesOrderLineNumber.

Primary analytical use:
- Reseller-channel revenue
- Product and category performance
- Territory performance
- Reseller performance
- Promotion analysis
- Profitability
- Internet-versus-reseller channel comparison

The exact uniqueness rules will be verified during profiling.

## FactProductInventory

**Proposed grain:** one product inventory record per ProductKey × DateKey, subject to source validation.

Primary analytical use:
- Inventory balance
- Inventory movement
- Units in
- Units out
- Unit cost
- Inventory value
- Product-level stock trends

Important source measures include:
- UnitCost
- UnitsIn
- UnitsOut
- UnitsBalance

## Modelling Rule

No DAX measure or Power BI visual will be treated as production-ready until the relevant fact table's grain, key uniqueness, null behaviour and referential integrity have been validated.
