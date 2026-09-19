# Stage 6 — DAX KPI Layer Validation Summary

## Status

Repository implementation and PostgreSQL benchmark reconciliation are complete.

Final exit gate still requires the live Power BI Desktop runtime query to return all checks as PASS.

## Governed semantic layer

Stage 6 provides a dedicated `KPI_Measures` table with **78 explicit report-facing measures** across:

- Sales & Volume
- Profitability
- Growth & Time Intelligence
- Role-Playing Dates
- Customer & Reseller
- Product
- Channel
- Promotion
- Inventory
- UX & Dynamic Titles

The semantic model discourages implicit measures. Technical fact columns remain hidden so report authors consume governed measures.

## PostgreSQL benchmark proof

GitHub Actions rebuilds the warehouse from the official source files and reconciles the Stage 6 KPI benchmarks directly against the `analytics` schema.

Verified benchmark values:

| KPI | PostgreSQL benchmark |
|---|---:|
| Total Sales | 109,809,274.2030 |
| Total Product Cost | 97,257,907.9547 |
| Gross Profit | 12,551,366.2483 |
| Units Sold | 274,776 |
| Distinct Orders | 31,455 |
| Customers | 18,484 |
| Repeat Customers | 6,865 |
| Resellers | 635 |
| Products Sold | 350 |
| Internet Sales | 29,358,677.2207 |
| Reseller Sales | 80,450,596.9823 |
| Discounted Sales | 5,422,689.0264 |
| Latest Inventory Date | 2014-06-30 |
| Current Inventory Value | 23,603,975.5700 |
| Current Inventory Units | 258,981 |
| Products With Inventory | 606 |
| Products Below Safety Stock | 543 |
| Products Below Reorder Point | 0 |
| Sales 2013 | 49,926,384.4972 |
| Sales 2014 | 45,694.7200 |
| Due-date Sales 2013 | 52,285,231.9952 |
| Ship-date Sales 2013 | 52,522,104.8347 |
| Gross Profit 2013 | 6,273,540.9644 |
| Gross Profit 2014 | 25,552.9376 |

## DAX policy checks

Repository validation enforces:

- weighted `Gross Margin % = Gross Profit / Total Sales`
- MTD/QTD/YTD and prior-year patterns against `DimDate[Date]`
- inactive Due Date and Ship Date activation with `USERELATIONSHIP`
- selection-aware product/category contribution and ranking
- latest-snapshot inventory logic
- neutral numeric currency formatting because no exchange-rate fact is in scope
- one display-folder assignment for every governed measure
- synchronized source and PBIP runtime QA files
- exactly **34 live exact runtime checks**

## Runtime gate

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage6_runtime.ps1
```

The script performs four gates in sequence:

1. PostgreSQL KPI reconciliation
2. DAX/TMDL contract validation
3. live Power BI exact KPI reconciliation (34 checks)
4. live Power BI all-measure smoke validation (78 measures)

The local verifier writes temporary evidence under the ignored `.runtime/` directory:

- `.runtime/stage6-powerbi-runtime-proof.csv`
- `.runtime/stage6-measure-smoke-proof.csv`

After the live gate passes, reviewed canonical copies are committed under `docs/data-engineering/`. Stage 6 is marked COMPLETE only after live evidence shows **34/34 exact KPI checks PASS** and **78/78 governed measures evaluate successfully**.


## Load-stability hardening

- `KPI_Measures` uses a one-row static M table so the measure host does not participate in calculated-table dependency evaluation.
- `FactInventory` uses a direct parameterized PostgreSQL SQL query instead of navigator lookup. This preserves the same imported columns while avoiding Power Query navigator evaluation cycles observed in Desktop.
