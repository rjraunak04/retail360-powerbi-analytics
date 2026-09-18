# Retail360 — Stage 3 Staging Validation

## Status

**PASSED — 18 September 2026**

Stage 3 was executed end to end in GitHub Actions against PostgreSQL 16 after the validated raw load.

## Transformation layer

The staging layer now provides:

- typed business dimensions
- flattened product hierarchy
- typed Internet sales
- typed Reseller sales
- a harmonised sales fact
- typed inventory
- derived gross profit and gross margin
- derived inventory movement and inventory value

## Validated row counts

| Object | Rows |
|---|---:|
| staging.fact_internet_sales | 60,398 |
| staging.fact_reseller_sales | 60,855 |
| staging.fact_sales | 121,253 |
| staging.fact_product_inventory | 776,286 |

## Quality results

The automated staging QA validates:

- all scoped dimension row counts
- source-to-staging fact row preservation
- unified sales-line grain uniqueness
- required grain fields
- product, date, customer, reseller, promotion, currency, territory and employee relationships
- inventory product/date relationships
- allowed channel values
- gross-profit formula consistency
- inventory-value formula consistency

The initial Stage 3 CI run passed all implemented checks. The strengthened QA suite is required to pass before merge.

## Key business rules

**Gross Profit**

`sales_amount - total_product_cost`

**Gross Margin %**

`gross_profit / sales_amount`

**Net Units Movement**

`units_in - units_out`

**Inventory Value**

`unit_cost * units_balance`

**Unified sales grain**

`channel + sales_order_number + sales_order_line_number`, represented by a unique `sales_line_id`.

## Stage 3 exit decision

After the strengthened CI suite passes, the staging layer is approved for the analytics star-schema build.

Next: **Stage 4 — Analytics Star Schema**.
