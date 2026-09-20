# Local Setup

This guide reproduces the PostgreSQL + Power BI project locally.

## Prerequisites

- Windows 10/11
- Git
- Python 3.11+
- Docker Desktop with WSL2 backend
- Power BI Desktop
- 8 GB RAM minimum; 16 GB recommended for comfortable Power BI + Docker work

## Clone and create the Python environment

```powershell
git clone https://github.com/rjraunak04/retail360-powerbi-analytics.git
cd retail360-powerbi-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Start PostgreSQL

```powershell
docker compose up -d postgres
docker compose ps
```

The compose configuration binds PostgreSQL to loopback for local development.

## Validate the warehouse

The GitHub Actions workflow contains the canonical rebuild order. The main local checks are:

```powershell
python scripts/validate_source_data.py
python scripts/qa_postgres_raw.py
python scripts/qa_staging.py
python scripts/qa_analytics.py
```

See `.github/workflows/postgres-stage2-ci.yml` for the full CI sequence.

## Open Power BI

```powershell
Start-Process .\powerbi\Retail360.pbip
```

The project uses Import mode and two Power Query parameters:

- `pServer`
- `pDatabase`

## Semantic-model runtime QA

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage6_runtime.ps1
```

The reviewed runtime evidence expects:

- 34/34 exact KPI checks
- 78/78 governed-measure smoke checks

## Report and enterprise QA

```powershell
python scripts/validate_stage7_report.py
python scripts/qa_stage8_edge_cases.py
python scripts/validate_stage8_enterprise.py
```

When Power BI Desktop is available:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_powerbi_stage8_runtime.ps1
```

## Packaging

```powershell
python scripts/validate_stage9_packaging.py --require-screenshots
powershell -ExecutionPolicy Bypass -File .\scripts\package_stage10_release.ps1
```

## Credentials

Do not commit database passwords, Power BI credentials or machine-local cache files. Use local environment variables or local credential storage for workstation-specific secrets.

## Troubleshooting

If Power BI loads stale model state:

1. save and close Power BI Desktop
2. ensure only one Desktop instance is running
3. remove repository-local `.pbi` cache directories if necessary
4. restart the PostgreSQL container
5. reopen `Retail360.pbip`

The source-controlled PBIP/TMDL/PBIR definitions remain the canonical project state.
