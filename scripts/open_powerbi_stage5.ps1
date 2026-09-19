param(
    [switch]$SkipWarehouseQa
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Retail360 Power BI local launcher" -ForegroundColor Cyan

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop engine is not available."
}

docker compose up -d postgres
if ($LASTEXITCODE -ne 0) {
    throw "Could not start PostgreSQL container."
}

$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    $status = docker inspect --format='{{.State.Health.Status}}' retail360-postgres 2>$null
    if ($status -eq "healthy") {
        $healthy = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    docker compose ps
    throw "PostgreSQL did not become healthy."
}

if (-not $SkipWarehouseQa) {
    python .\scripts\qa_postgres_raw.py
    if ($LASTEXITCODE -ne 0) { throw "Raw warehouse QA failed." }

    python .\scripts\qa_staging.py
    if ($LASTEXITCODE -ne 0) { throw "Staging QA failed." }

    python .\scripts\qa_analytics.py
    if ($LASTEXITCODE -ne 0) { throw "Analytics QA failed." }
}

python .\scripts\validate_semantic_model.py
if ($LASTEXITCODE -ne 0) { throw "Semantic contract validation failed." }

python .\scripts\validate_pbip_project.py
if ($LASTEXITCODE -ne 0) { throw "PBIP scaffold validation failed." }

$Project = Join-Path $Root "powerbi\Retail360.pbip"
Write-Host "Opening: $Project" -ForegroundColor Green
Start-Process $Project

Write-Host ""
Write-Host "Power BI project opened." -ForegroundColor Green
Write-Host "The model definition is already in PBIP/TMDL format; no TMDL copy/paste is required."
Write-Host "On the first refresh, Power BI may request the local PostgreSQL credential."
