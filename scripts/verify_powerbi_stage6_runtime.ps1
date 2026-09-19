param()

$Root = Split-Path -Parent $PSScriptRoot
$BaseVerifier = Join-Path $Root "scripts\verify_powerbi_stage5_runtime.ps1"
$Query = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage6 KPI QA.dax"
$Proof = Join-Path $Root "docs\data-engineering\stage6-powerbi-runtime-proof.csv"

if (-not (Test-Path $BaseVerifier)) {
    throw "Base Power BI runtime verifier is missing."
}

# Stage6 QA intentionally has 20 rows and includes the core check names the
# generic verifier uses to identify the Retail360 model.
& powershell -ExecutionPolicy Bypass -File $BaseVerifier -QueryPath $Query -ProofCsvPath $Proof -StageLabel "Stage 6"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Stage 6 runtime proof written to: $Proof" -ForegroundColor Green
