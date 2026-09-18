# Retail360 — Stage 4 Analytics Star-Schema Validation

## Status

**PASSED — 18 September 2026**

Stage 4 was executed end to end in GitHub Actions against PostgreSQL 16 after the raw and staging layers passed their quality gates.

## Final Power BI-facing tables

### Facts

- `analytics.fact_sales` — one unified Internet/Reseller sales order line
- `analytics.fact_inventory` — one Product × Date inventory snapshot

### Conformed dimensions

- `analytics.dim_date`
- `analytics.dim_product`
- `analytics.dim_customer`
- `analytics.dim_reseller`
- `analytics.dim_employee`
- `analytics.dim_geography`
- `analytics.dim_sales_territory`
- `analytics.dim_promotion`
- `analytics.dim_currency`
- `analytics.dim_channel`

## Validation results

- FactSales rows: **121,253**
- FactInventory rows: **776,286**
- Internet sales lines: **60,398**
- Reseller sales lines: **60,855**
- duplicate sales grain: **0**
- duplicate inventory grain: **0**
- null FactSales foreign keys: **0**
- invalid channel keys: **0**
- channel applicability errors: **0**
- unknown/not-applicable members validated
- fact foreign-key constraints: **14/14 present**
- metric-preservation checks: **6/6 PASS**

## Metric preservation

The analytics build preserved the staging business totals exactly:

| Metric | Validated value |
|---|---:|
| Total Sales | 109,809,274.2030 |
| Total Product Cost | 97,257,907.9547 |
| Gross Profit | 12,551,366.2483 |
| Units Sold | 274,776 |
| Distinct Orders | 31,455 |
| Inventory Value across all snapshots | 29,713,024,789.8300 |

All staging → analytics differences for the tested additive measures were exactly zero.

## Modelling decisions validated

- Internet and Reseller sales are harmonised into one FactSales.
- Channel is represented by a conformed DimChannel.
- Customer applies to Internet sales; Reseller and Employee apply to Reseller sales.
- Key 0 is used for Unknown / Not Applicable members to avoid nullable fact foreign keys.
- Customer/Reseller geography is resolved directly onto FactSales.
- Product category and subcategory are flattened into DimProduct.
- FactInventory remains separate because its Product × Date snapshot grain differs from the sales-line grain.
- Date and Product are conformed dimensions shared by Sales and Inventory.
- Order Date is the intended active Power BI date relationship; Due Date and Ship Date are role-playing relationships.

## Performance layer

The analytics schema includes:

- physical report-facing tables
- dimension primary keys
- fact foreign keys
- fact grain primary keys
- indexes on common FactSales filter/join columns
- FactInventory date index
- PostgreSQL `ANALYZE` statistics refresh

## Stage 4 exit decision

The dimensional warehouse layer is approved for Power BI semantic-model development.

Next: **Stage 5 — Power BI Semantic Model**.
