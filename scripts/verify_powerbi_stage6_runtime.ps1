param()

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$BaseVerifier = Join-Path $Root "scripts\verify_powerbi_stage5_runtime.ps1"
$Query = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage6 KPI QA.dax"
$Proof = Join-Path $Root "docs\data-engineering\stage6-powerbi-runtime-proof.csv"

foreach ($required in @(
    $BaseVerifier,
    $Query,
    (Join-Path $Root "scripts\qa_stage6_kpis.py"),
    (Join-Path $Root "scripts\validate_stage6_dax.py")
)) {
    if (-not (Test-Path $required)) {
        throw "Required Stage 6 validation artifact is missing: $required"
    }
}

Write-Host "Retail360 Stage 6 full validation gate" -ForegroundColor Cyan
Write-Host "1/3 PostgreSQL KPI reconciliation..." -ForegroundColor DarkGray
python scripts/qa_stage6_kpis.py
if ($LASTEXITCODE -ne 0) {
    throw "Stage 6 PostgreSQL KPI reconciliation failed."
}

Write-Host "2/3 DAX/TMDL contract validation..." -ForegroundColor DarkGray
python scripts/validate_stage6_dax.py
if ($LASTEXITCODE -ne 0) {
    throw "Stage 6 DAX/TMDL contract validation failed."
}

Write-Host "3/3 Live Power BI semantic-model runtime validation..." -ForegroundColor DarkGray
& powershell -ExecutionPolicy Bypass -File $BaseVerifier -QueryPath $Query -ProofCsvPath $Proof -StageLabel "Stage 6"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "STAGE 6 FULL VALIDATION PASSED." -ForegroundColor Green
Write-Host "Runtime proof written to: $Proof" -ForegroundColor Green
