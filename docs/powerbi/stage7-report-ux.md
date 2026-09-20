# Stage 7 — Recruiter-Grade Report UX

## Status

**COMPLETE.** The source-controlled PBIR implementation is complete and CI-validated. Pixel-level screenshot/aesthetic review is treated as a Stage 8 QA activity rather than a Stage 7 build blocker.

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

- exact **62** visual-container inventory (6 per visible page + 2 tooltip visuals)
- page-purpose annotations and visible-page title textboxes
- contiguous tab order and unique z-order

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

## Stage 7 exit decision

Stage 7 is complete when the PBIR source contract and full CI pipeline are green. The report definition is deterministic and source-controlled, with 10 visible pages, one tooltip page, 62 validated visual containers, drillthrough, tooltip bindings, governed measures, layout geometry, and interaction contracts.

Pixel-perfect screenshot review, Performance Analyzer review, accessibility refinements, and final render tuning belong to **Stage 8 — Enterprise Features and QA**. This keeps Stage 7 focused on building the recruiter-grade report experience and Stage 8 focused on runtime quality assurance.
