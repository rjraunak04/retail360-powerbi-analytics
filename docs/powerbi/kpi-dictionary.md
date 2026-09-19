# Retail360 — KPI Dictionary

Stage 6 centralizes report logic in the dedicated `Measures` table. Report visuals should use these explicit measures rather than implicit column aggregations.

## Sales & Volume

| Measure | Business definition |
|---|---|
| Total Sales | Sum of sales amount in the current filter context. |
| Units Sold | Sum of order quantity. |
| Sales Lines | Count of harmonized sales lines. |
| Distinct Orders | Distinct order count using Channel + Sales Order Number so Internet and Reseller order identifiers cannot collide. |
| Average Selling Price | Total Sales / Units Sold. |
| Average Order Value | Total Sales / Distinct Orders. |
| Average Units per Order | Units Sold / Distinct Orders. |
| Total Discount Amount | Sum of line discount amount. |
| Discount Rate | Discount Amount / pre-discount Extended Amount. |
| Total Tax | Sum of tax amount. |
| Total Freight | Sum of freight amount. |

## Profitability

| Measure | Business definition |
|---|---|
| Total Product Cost | Sum of total product cost for sold lines. |
| Gross Profit | Sum of warehouse-derived Sales Amount - Total Product Cost. |
| Gross Margin % | Gross Profit / Total Sales. This is a weighted margin and intentionally does **not** average row-level margin percentages. |
| Profit per Unit | Gross Profit / Units Sold. |
| Profit per Order | Gross Profit / Distinct Orders. |

## Growth & Time Intelligence

Sales MTD/QTD/YTD, prior-year, YoY absolute/percentage, previous-month, MoM absolute/percentage, Profit YTD/PY/YoY, and Units YTD/PY/YoY use the marked `DimDate[Date]` table.

## Role-Playing Dates

`Sales by Due Date`, `Sales by Ship Date`, `Orders by Due Date`, and `Orders by Ship Date` activate the inactive warehouse date relationships through `USERELATIONSHIP`.

## Customer & Reseller

Customer and reseller counts exclude key 0 (Not Applicable/Unknown). Repeat customers are customers with more than one distinct order in the current context.

## Product

Product and category share measures respect the user's current selections through `ALLSELECTED`. Rank measures use `RANKX` and are intended for Top-N and detail tables.

## Channel

Internet and Reseller measures split the harmonized fact through `DimChannel`. At the all-channel level, Internet Sales + Reseller Sales must reconcile to Total Sales.

## Promotion

Discount-focused measures use actual positive `Discount Amount` on sales rows. The project intentionally does not claim causal promotion lift because there is no experiment/counterfactual design.

## Inventory

Inventory is a snapshot fact. Headline inventory KPIs therefore use the latest available snapshot rather than summing inventory value across all historical dates.

- Current Inventory Value / Units: latest snapshot
- Average Inventory Value: average daily snapshot value in the selected period
- Inventory Turnover: Total Product Cost / Average Inventory Value
- Products Below Safety Stock / Reorder Point: latest-snapshot product risk counts
- Inventory Health %: 1 - Products Below Reorder Point / Products With Inventory

## Currency note

AdventureWorks facts contain CurrencyKey but this project scope does not load currency-rate history. For that reason Stage 6 uses neutral numeric formats rather than labeling consolidated sales/profit totals as USD.
