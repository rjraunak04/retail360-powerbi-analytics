# Retail360 — Stage 8 Performance Review

## Scope

The report is an Import-mode PBIP/TMDL model with 10 visible report pages plus one hidden tooltip page. Stage 8 reviews performance at three levels: report structure, DAX design, and runtime evidence.

## Report-structure findings

The Stage 7 PBIR contract already limits each visible page to six native visuals and the tooltip page to two visuals. No custom visuals are required. This keeps visual fan-out predictable and avoids pages with dozens of independent queries.

The report uses native cards, slicers, line charts, bar charts and tables. Report visuals bind to explicit governed measures from `KPI_Measures`; implicit measures are discouraged at model level.

## DAX review

Accepted patterns:

- base measures are reused instead of repeating business logic
- `Gross Margin %` is weighted using `DIVIDE([Gross Profit], [Total Sales])`
- ratio measures use `DIVIDE`
- channel filters use `KEEPFILTERS`
- due/ship analysis uses inactive relationships with `USERELATIONSHIP`
- inventory headline measures first resolve a single latest snapshot date
- product contribution/ranking uses `ALLSELECTED` so report selections remain meaningful

Known higher-cost measures that are retained because they are business-correct and used selectively:

- `Distinct Orders`: composite Channel + Sales Order grain requires `SUMMARIZE`
- `Product Rank by Sales` / `Category Rank by Sales`: `RANKX`
- inventory risk counts: iterate visible products on the latest snapshot

These measures should not be duplicated across many visuals on the same page.

## Performance Analyzer review policy

For a local Desktop review:

1. Open the canonical `powerbi/Retail360.pbip`.
2. Use Optimize → Performance Analyzer.
3. Start recording.
4. Navigate each visible page once with default filters.
5. Refresh visuals on the Executive Overview, Product & Profitability and Inventory Analytics pages.
6. Investigate any single visual whose DAX/query duration is materially slower than peers.
7. Save an export or screenshot under `.runtime/`; runtime evidence is intentionally not committed unless reviewed.

The CI gate cannot reproduce Desktop rendering time, so it validates the structural performance contract instead: visual count, native visual types, explicit measures, relationship direction, Import mode and governed DAX patterns.

## Optimization decisions

Stage 8 does not add speculative calculated columns, bidirectional relationships, or duplicated aggregation tables. The existing star schema and explicit-measure layer remain the performance baseline. Performance changes should be evidence-driven after a measured Desktop trace.
