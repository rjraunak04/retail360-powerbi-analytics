param(
    [switch]$SkipStage6Regression
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Stage6Verifier = Join-Path $Root "scripts\verify_powerbi_stage6_runtime.ps1"
$BaseVerifier = Join-Path $Root "scripts\verify_powerbi_stage5_runtime.ps1"

$required = @(
    $Stage6Verifier,
    $BaseVerifier,
    (Join-Path $Root "scripts\qa_stage8_enterprise.py"),
    (Join-Path $Root "scripts\validate_stage8_enterprise.py")
)
foreach ($path in $required) {
    if (-not (Test-Path $path)) {
        throw "Missing Stage 8 validation artifact: $path"
    }
}

Write-Host "Retail360 Stage 8 enterprise validation gate" -ForegroundColor Cyan

Write-Host "1/4 Stage 8 PostgreSQL edge-case QA..." -ForegroundColor DarkGray
python scripts/qa_stage8_enterprise.py
if ($LASTEXITCODE -ne 0) { throw "Stage 8 PostgreSQL edge-case QA failed." }

Write-Host "2/4 Stage 8 enterprise semantic/report contract..." -ForegroundColor DarkGray
python scripts/validate_stage8_enterprise.py
if ($LASTEXITCODE -ne 0) { throw "Stage 8 enterprise contract validation failed." }

if (-not $SkipStage6Regression) {
    Write-Host "3/4 Stage 6 semantic-model regression gate..." -ForegroundColor DarkGray
    # Reuse the single healthy open Retail360 Desktop instance when present.
    # Stage 6 already validates the model through live 34-check + 78-measure
    # gates, so forcing a restart here is unnecessary and can block on an open
    # Power BI window or Save dialog.
    & powershell -ExecutionPolicy Bypass -File $Stage6Verifier
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
else {
    Write-Host "3/4 Stage 6 regression gate skipped by request." -ForegroundColor Yellow
}

Write-Host "4/4 Stage 8 live regional RLS validation..." -ForegroundColor DarkGray

$Runtime = Join-Path $Root ".runtime"
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

$roleTests = @(
    @{ Role = "RLS_North_America"; Query = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage8 RLS North America QA.dax"; Proof = Join-Path $Runtime "stage8-rls-north-america-proof.csv"; Label = "Stage 8 RLS North America" },
    @{ Role = "RLS_Europe"; Query = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage8 RLS Europe QA.dax"; Proof = Join-Path $Runtime "stage8-rls-europe-proof.csv"; Label = "Stage 8 RLS Europe" },
    @{ Role = "RLS_Pacific"; Query = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage8 RLS Pacific QA.dax"; Proof = Join-Path $Runtime "stage8-rls-pacific-proof.csv"; Label = "Stage 8 RLS Pacific" }
)

$passedRoles = 0
foreach ($test in $roleTests) {
    Write-Host ("Validating role " + $test.Role + "...") -ForegroundColor DarkGray
    $invokeArgs = @(
        "-ExecutionPolicy", "Bypass",
        "-File", $BaseVerifier,
        "-StartupTimeoutSeconds", "120",
        "-ModelProbeTimeoutSeconds", "60",
        "-QueryPath", $test.Query,
        "-ProofCsvPath", $test.Proof,
        "-StageLabel", $test.Label,
        "-RoleName", $test.Role,
        "-MinimumRows", "5",
        "-RequiredCheck", "Total Sales"
    )
    & powershell @invokeArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $passedRoles++
}

$stage6Status = if ($SkipStage6Regression) { "SKIPPED" } else { "PASS" }
Write-Host ""
Write-Host "STAGE 8 FULL VALIDATION PASSED." -ForegroundColor Green
Write-Host "Enterprise SQL / edge-case QA: PASS" -ForegroundColor Green
Write-Host "Semantic / relationship / DAX QA: PASS" -ForegroundColor Green
Write-Host ("Stage 6 regression gate: " + $stage6Status) -ForegroundColor Green
Write-Host ("Regional RLS roles: " + $passedRoles + "/3 PASS") -ForegroundColor Green
Write-Host "Performance-review contract: PASS" -ForegroundColor Green
Write-Host ("Runtime evidence folder: " + $Runtime) -ForegroundColor Green
