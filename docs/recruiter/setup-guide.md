# Retail360 — Reproducible Setup Guide

This guide reproduces the local PostgreSQL + Power BI project from the repository.

## Prerequisites

- Windows 10/11
- Git
- Python 3.11+
- Docker Desktop with WSL2 backend
- Power BI Desktop
- 8 GB RAM minimum; 16 GB recommended for comfortable Power BI + Docker work

## 1. Clone

```powershell
git clone https://github.com/rjraunak04/retail360-powerbi-analytics.git
cd retail360-powerbi-analytics
```

## 2. Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Start PostgreSQL

```powershell
docker compose up -d postgres
docker compose ps
```

The compose configuration binds PostgreSQL to loopback for local development.

## 4. Build / validate warehouse

The GitHub Actions workflow contains the canonical rebuild order. Locally, the main validation scripts can be run in the same logical sequence:

```powershell
python scripts/validate_source_data.py
python scripts/qa_postgres_raw.py
python scripts/qa_staging.py
python scripts/qa_analytics.py
```

See the workflow file for the exact CI sequence and environment setup.

## 5. Open Power BI

```powershell
Start-Process .\powerbi\Retail360.pbip
```

The PBIP project references the source-controlled semantic model and report definitions.

Power Query parameters:

- `pServer`
- `pDatabase`

The project uses Import mode.

## 6. Stage 6 semantic runtime QA

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage6_runtime.ps1
```

Expected exit gate:

- 34/34 exact KPI checks PASS
- 78/78 governed-measure smoke checks PASS

Canonical reviewed evidence is committed under `docs/data-engineering/`.

## 7. Stage 7 / 8 QA

```powershell
python scripts/validate_stage7_report.py
python scripts/qa_stage8_edge_cases.py
python scripts/validate_stage8_enterprise.py
```

If available in the local environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage8_runtime.ps1
```

## 8. Screenshot capture for portfolio

With the report fully loaded in Power BI Desktop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_stage9_screenshots.ps1
```

The script writes report screenshots to `docs/screenshots/`.

## 9. Packaging validation

```powershell
python scripts/validate_stage9_packaging.py
```

## Credentials

Do not commit database passwords, Power BI credentials or machine-local cache files.

Use environment variables / local credential storage for workstation-specific secrets.

## Troubleshooting

If Power BI reports stale model errors:

1. save and close Power BI Desktop
2. ensure only one Desktop instance is running
3. remove repository-local `.pbi` cache directories if necessary
4. restart the local PostgreSQL container
5. reopen `Retail360.pbip`

The source-controlled PBIP/TMDL/PBIR definitions remain the canonical project state.
