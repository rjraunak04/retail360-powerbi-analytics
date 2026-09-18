# Retail360 — Dimensional Modelling Decisions

## Key strategy

AdventureWorksDW already supplies stable integer warehouse keys. Retail360 reuses these source surrogate keys in the analytics layer rather than generating a second unnecessary surrogate-key system.

Key `0` is reserved for Unknown / Not Applicable members.

## Sales unification

Internet and Reseller sales have compatible commercial measures, so they are combined into one `analytics.fact_sales` table.

A dedicated `dim_channel` distinguishes the source business channel.

The unified model retains channel-specific dimensions:

- Customer applies to Internet sales.
- Reseller and Employee apply to Reseller sales.
- Key 0 handles the non-applicable side of each channel without nullable relationships.

## Geography

Source geography is reached through Customer for Internet sales and through Reseller for Reseller sales.

Retail360 resolves that geography during the analytics build and stores `geography_key` directly on FactSales. This avoids a Customer → Geography or Reseller → Geography snowflake in the Power BI model.

## Product hierarchy

Category and Subcategory labels are denormalised into DimProduct. This is deliberate for a semantic model: it simplifies hierarchy navigation, filtering and report performance.

## Inventory

FactInventory remains a separate fact because its grain is Product × Date snapshot, which is fundamentally different from the transactional sales-line grain.

Sales and inventory share conformed Date and Product dimensions.
