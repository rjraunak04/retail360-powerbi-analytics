# Repository Packaging Validation

## Purpose

This check keeps the public repository focused on the technical project rather than job-application material.

Validated artifacts include:

- README
- architecture and star-schema diagrams
- KPI dictionary
- business-analysis SQL examples
- architecture decisions
- reproducible setup guide
- rendered dashboard screenshots
- Stage 6 runtime evidence
- Stage 8 enterprise QA
- automated packaging validation

## Evidence

The packaging layer references existing engineering evidence rather than duplicating claims:

- Stage 6 exact Power BI runtime proof — 34/34 PASS
- Stage 6 governed-measure smoke proof — 78/78 PASS
- Stage 7 report source contract — 10 visible pages + 1 hidden tooltip
- Stage 8 enterprise/security/edge-case QA
- 10/10 rendered dashboard screenshots

## Screenshot gate

```powershell
python scripts/validate_stage9_packaging.py --require-screenshots
```

The repository uses actual Power BI Desktop renders under `docs/screenshots/`; generated dashboard mockups are not used as evidence.

## Status

Packaging validation is complete when CI passes and all ten rendered screenshots pass the file-size sanity check.
