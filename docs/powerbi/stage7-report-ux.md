# Stage 7 — Recruiter-Grade Report UX

## Status

Source-controlled PBIR implementation is complete and validated in CI.

## Report architecture

Retail360 now contains **10 visible analytical pages** plus **1 hidden report-page tooltip**:

1. Executive Overview
2. Sales & Growth
3. Product & Profitability
4. Customer Analytics
5. Channel / Reseller Analytics
6. Geography & Territory
7. Promotion Analysis
8. Inventory Analytics
9. Drill-through Detail
10. Model / Data Quality
11. Product Tooltip — hidden in view mode

## UX system

The report uses a consistent 1280×720 canvas with an 8/16/24-pixel spacing rhythm:

- title and inline slicer band
- one multi-value KPI strip
- primary analytical visual on the left
- supporting ranking/detail visual on the right
- native Power BI page tabs for navigation

All visible pages use the same placement grid so recruiters can scan the report without relearning the layout.

## Visual design

The PBIR definition uses current native visual types:

- `cardVisual` for multi-KPI strips
- `lineChart` for time trends
- `barChart` for category/ranking analysis
- `tableEx` for exact lookup/detail
- `slicer` in Dropdown mode for compact filtering
- `textbox` for page titles and analytical framing

Deprecated legacy card/map visuals are not used.

## Interaction design

- Year slicer is consistently placed in the header band.
- A second context slicer changes by analytical page.
- Native visual interactions remain enabled unless Power BI defaults dictate otherwise.
- A dedicated Product drillthrough page accepts `DimProduct[Product Name]`.
- A hidden Product Tooltip page carries product context and headline profitability measures.
- Drillthrough pages keep report filter context.

## Semantic policy

All report-facing calculations use explicit governed measures from `KPI_Measures`.

No visual directly recreates business KPI formulas.

Consolidated monetary measures intentionally remain currency-symbol neutral because the current project scope has no historical currency-rate fact.

## Validation

Run:

```powershell
python scripts/validate_stage7_report.py
```

The validator checks:

- exact page inventory/order
- visible vs hidden tooltip pages
- valid page and visual IDs
- page bounds and accidental overlaps
- required visual-type coverage
- semantic-model column bindings
- governed KPI measure bindings
- card/slicer role correctness
- table grow-to-fit configuration
- drillthrough filter/pageBinding integrity
- report-page tooltip binding

GitHub Actions runs this validation after Stage 6 semantic/DAX checks.

## Desktop render gate

PBIR source validation is deterministic and CI-backed. Final pixel-level review still requires Power BI Desktop to render the report on a machine with enough free RAM. The local host previously reported only 0.56 GB free memory, so screenshot/pixel review should be performed only after memory pressure is cleared.
