param()

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$BaseVerifier = Join-Path $Root "scripts\verify_powerbi_stage5_runtime.ps1"
$ExactQuery = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage6 KPI QA.dax"
$SmokeQuery = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage6 Measure Smoke QA.dax"
$ExactProof = Join-Path $Root ".runtime\stage6-powerbi-runtime-proof.csv"
$SmokeProof = Join-Path $Root ".runtime\stage6-measure-smoke-proof.csv"

foreach ($required in @(
    $BaseVerifier,
    $ExactQuery,
    $SmokeQuery,
    (Join-Path $Root "scripts\qa_stage6_kpis.py"),
    (Join-Path $Root "scripts\validate_stage6_dax.py")
)) {
    if (-not (Test-Path $required)) {
        throw "Required Stage 6 validation artifact is missing: $required"
    }
}

Write-Host "Retail360 Stage 6 full validation gate" -ForegroundColor Cyan

Write-Host "Starting/checking PostgreSQL..." -ForegroundColor DarkGray
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    $DockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $DockerDesktop) {
        Write-Host "Docker Desktop is not running; starting it automatically..." -ForegroundColor Yellow
        Start-Process $DockerDesktop
        $dockerReady = $false
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Seconds 2
            docker info *> $null
            if ($LASTEXITCODE -eq 0) {
                $dockerReady = $true
                break
            }
        }
        if (-not $dockerReady) {
            throw "Docker Desktop did not become ready within 60 seconds."
        }
    }
    else {
        throw "Docker Desktop is not running and its standard executable path was not found."
    }
}
docker compose up -d postgres | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "Could not start the Retail360 PostgreSQL container."
}

$PgUser = if ($env:PGUSER) { $env:PGUSER } else { "postgres" }
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    docker compose exec -T postgres pg_isready -U $PgUser *> $null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "Retail360 PostgreSQL did not become ready within 60 seconds."
}

Write-Host "1/4 PostgreSQL KPI reconciliation..." -ForegroundColor DarkGray
python scripts/qa_stage6_kpis.py
if ($LASTEXITCODE -ne 0) { throw "Stage 6 PostgreSQL KPI reconciliation failed." }

Write-Host "2/4 DAX/TMDL contract validation..." -ForegroundColor DarkGray
python scripts/validate_stage6_dax.py
if ($LASTEXITCODE -ne 0) { throw "Stage 6 DAX/TMDL contract validation failed." }

Write-Host "Preparing a fresh Power BI Stage 6 runtime instance..." -ForegroundColor DarkGray

# The user may already have Retail360 open from Stage 5. Power BI Desktop does
# not hot-reload TMDL files into an already-running semantic model. To avoid
# validating stale in-memory metadata, open a clean runtime copy of the current
# source-controlled PBIP project. This does not close or modify the user's
# existing Power BI window.
$RuntimeRoot = Join-Path $Root ".runtime"
New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

$RuntimeProjectDir = Join-Path $RuntimeRoot "stage6-powerbi-fresh"
if (Test-Path $RuntimeProjectDir) {
    try {
        Remove-Item $RuntimeProjectDir -Recurse -Force -ErrorAction Stop
    }
    catch {
        $RuntimeProjectDir = Join-Path $RuntimeRoot ("stage6-powerbi-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    }
}

Copy-Item (Join-Path $Root "powerbi") $RuntimeProjectDir -Recurse -Force

# Never reuse local Power BI caches from the original project.
Get-ChildItem $RuntimeProjectDir -Directory -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq ".pbi" } |
    Sort-Object FullName -Descending |
    ForEach-Object {
        try { Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop } catch {}
    }

$FreshProject = Join-Path $RuntimeProjectDir "Retail360.pbip"
if (-not (Test-Path $FreshProject)) {
    throw "Fresh Stage 6 PBIP runtime copy was not created: $FreshProject"
}

$BeforeEnginePids = @(
    Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue |
        ForEach-Object { [int]$_.ProcessId }
)

Write-Host "Opening fresh Stage 6 PBIP from current branch..." -ForegroundColor Yellow
Start-Process $FreshProject

$FreshEngineStarted = $false
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 2
    $CurrentEnginePids = @(
        Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue |
            ForEach-Object { [int]$_.ProcessId }
    )
    $NewEnginePids = @($CurrentEnginePids | Where-Object { $BeforeEnginePids -notcontains $_ })
    if ($NewEnginePids.Count -gt 0) {
        $FreshEngineStarted = $true
        break
    }
}

if (-not $FreshEngineStarted) {
    Write-Host "No new engine PID detected yet; continuing with semantic-model discovery because Power BI may have reused its host process." -ForegroundColor Yellow
}

# Give Desktop a short settling window after the model engine appears.
Start-Sleep -Seconds 5

Write-Host "3/4 Live Power BI KPI reconciliation..." -ForegroundColor DarkGray
& powershell -ExecutionPolicy Bypass -File $BaseVerifier -StartupTimeoutSeconds 120 -ModelProbeTimeoutSeconds 120 -QueryPath $ExactQuery -ProofCsvPath $ExactProof -StageLabel "Stage 6 KPI reconciliation"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "4/4 Live Power BI all-measure smoke test..." -ForegroundColor DarkGray
& powershell -ExecutionPolicy Bypass -File $BaseVerifier -StartupTimeoutSeconds 120 -ModelProbeTimeoutSeconds 120 -QueryPath $SmokeQuery -ProofCsvPath $SmokeProof -StageLabel "Stage 6 measure smoke"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "STAGE 6 FULL VALIDATION PASSED." -ForegroundColor Green
Write-Host "Exact KPI proof:   $ExactProof" -ForegroundColor Green
Write-Host "Measure smoke proof: $SmokeProof" -ForegroundColor Green
