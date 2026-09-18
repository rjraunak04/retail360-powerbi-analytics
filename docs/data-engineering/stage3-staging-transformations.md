# Stage 3 — Staging and Business Transformation

## Objective

Convert the source-preserving PostgreSQL raw layer into typed, business-friendly staging objects that are safe to use for downstream dimensional modelling.

## Design

The raw layer remains unchanged. Stage 3 exposes PostgreSQL views in the `staging` schema.

### Typed dimensions

- `staging.dim_date`
- `staging.dim_currency`
- `staging.dim_sales_territory`
- `staging.dim_geography`
- `staging.dim_product`
- `staging.dim_customer`
- `staging.dim_reseller`
- `staging.dim_promotion`
- `staging.dim_employee`

The product view flattens Product → Subcategory → Category names to reduce downstream snowflaking.

### Typed facts

- `staging.fact_internet_sales`
- `staging.fact_reseller_sales`
- `staging.fact_sales` — harmonised Internet + Reseller sales
- `staging.fact_product_inventory`

## Business transformations

Stage 3 introduces:

- strongly typed integer/date/numeric fields
- business-friendly English names
- a common `channel` attribute
- globally unique `sales_line_id`
- gross profit = sales amount − total product cost
- gross margin % = gross profit / sales amount
- inventory net movement = units in − units out
- inventory value = unit cost × units balance

## Null policy

Blank source strings become SQL NULL for typed business fields. Raw records remain preserved in the `raw` schema.

## Validation gate

Automated QA requires:

- source-to-staging row preservation
- unique unified sales-line grain
- no null required sales grain fields
- no product/date/customer/reseller orphans
- correct gross-profit calculations
- correct inventory-value calculations

Run:

```powershell
python .\scripts\apply_staging.py
python .\scripts\qa_staging.py
```
