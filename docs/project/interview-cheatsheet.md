# Retail360 — Interview Cheat Sheet

## Start here

**Problem:** leadership needs one governed view of retail sales, profit, customers, products, channels, territories, promotions and inventory.

**Stack:** PostgreSQL 16, SQL, Python, Power Query, Power BI, PBIP/TMDL/PBIR, DAX, Docker, GitHub Actions.

**Model:** FactSales + FactInventory with conformed dimensions.

**Scale:** 121,253 sales lines; 776,286 inventory snapshots; 78 governed measures; 10 visible report pages + 1 tooltip.

## Five technical sentences

1. FactSales is one harmonised sales-order-line grain across Internet and Reseller channels.
2. FactInventory is Product × Date snapshot grain and is intentionally separate from transactional sales.
3. Order Date is active; Due Date and Ship Date are role-playing inactive relationships activated through DAX.
4. Gross Margin % is weighted as Gross Profit / Total Sales, while current inventory uses only the latest snapshot.
5. SQL benchmark checks, live DAX checks, RLS QA, PBIR validation and CI make the project reproducible.

## Numbers

- Sales: 109.81M
- Gross Profit: 12.55M
- Orders: 31,455
- Units: 274,776
- Customers: 18,484
- Resellers: 635
- Internet Sales: 29.36M
- Reseller Sales: 80.45M
- Current Inventory Value: 23.60M
- Current Inventory Units: 258,981

## Best debugging story

Stage 6 originally surfaced Power BI Desktop integration issues around stale semantic-model instances, a reserved measure-host table name and low-memory runtime retries. I fixed the architecture by keeping the Stage 5 source partitions frozen, using a safe static `KPI_Measures` host, reducing duplicate local Analysis Services engines, and validating the final model with SQL reconciliation plus live DAX runtime gates.

## Best modelling story

Inventory is the strongest example of why grain matters. Sales is transactional while inventory is periodic. Keeping them as separate facts prevents invalid joins and allows current-state measures to deliberately select the latest inventory snapshot.

## Best governance story

The project avoids unsupported claims: no causal promotion lift, no fake USD conversion without FX history, no claim of Power BI Service publication without tenant evidence, and no territory RLS on inventory because that fact has no territory grain.
