param(
    [string]$QueryPath = "",
    [string]$ProofCsvPath = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not $QueryPath) {
    $QueryPath = Join-Path $Root "powerbi\Retail360.SemanticModel\DAXQueries\Stage5 Model QA.dax"
}
if (-not $ProofCsvPath) {
    $ProofCsvPath = Join-Path $Root "docs\data-engineering\stage5-powerbi-runtime-proof.csv"
}

if (-not (Test-Path $QueryPath)) {
    throw "Stage 5 DAX QA query not found: $QueryPath"
}

Write-Host "Retail360 Stage 5 Power BI runtime verifier" -ForegroundColor Cyan
Write-Host "Searching for the open Power BI Desktop semantic model..." -ForegroundColor DarkGray

$msmdsrv = Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'"
if (-not $msmdsrv) {
    throw "No Power BI Analysis Services process (msmdsrv.exe) is running. Open Retail360.pbip in Power BI Desktop first."
}

function Get-PowerBIPort {
    param([string]$CommandLine)

    if (-not $CommandLine) { return $null }

    $match = [regex]::Match($CommandLine, '-s\s+"([^"]+)"')
    if (-not $match.Success) {
        $match = [regex]::Match($CommandLine, '-s\s+([^\s]+)')
    }
    if (-not $match.Success) { return $null }

    $workspace = $match.Groups[1].Value.Trim('"')
    $candidates = @(
        (Join-Path $workspace "msmdsrv.port.txt"),
        (Join-Path $workspace "Data\msmdsrv.port.txt")
    )

    foreach ($portFile in $candidates) {
        if (Test-Path $portFile) {
            try {
                # Power BI commonly writes the file as UTF-16; Get-Content also
                # handles current text encodings correctly in modern Desktop.
                $raw = (Get-Content $portFile -Raw).Trim([char]0).Trim()
                if ($raw -match '^\d+$') { return [int]$raw }

                $bytes = [System.IO.File]::ReadAllBytes($portFile)
                $unicode = [System.Text.Encoding]::Unicode.GetString($bytes).Trim([char]0).Trim()
                if ($unicode -match '^\d+$') { return [int]$unicode }
            }
            catch {
                continue
            }
        }
    }
    return $null
}

function Open-AdodbConnection {
    param([int]$Port)

    $conn = New-Object -ComObject ADODB.Connection
    $conn.CommandTimeout = 120
    $conn.ConnectionTimeout = 15
    $conn.Open("Provider=MSOLAP;Data Source=localhost:$Port;Integrated Security=SSPI;")
    return $conn
}

function Recordset-ToObjects {
    param($Recordset)

    $rows = New-Object System.Collections.Generic.List[object]
    while (-not $Recordset.EOF) {
        $row = [ordered]@{}
        for ($i = 0; $i -lt $Recordset.Fields.Count; $i++) {
            $field = $Recordset.Fields.Item($i)
            $row[$field.Name] = $field.Value
        }
        $rows.Add([pscustomobject]$row)
        $Recordset.MoveNext()
    }
    return $rows
}

$selectedConnection = $null
$selectedPort = $null

foreach ($proc in $msmdsrv) {
    $port = Get-PowerBIPort -CommandLine $proc.CommandLine
    if (-not $port) { continue }

    try {
        $conn = Open-AdodbConnection -Port $port
        $probe = $conn.Execute('EVALUATE ROW("FactSales Rows", COUNTROWS(FactSales))')
        $probeRows = Recordset-ToObjects -Recordset $probe
        $probe.Close()

        if ($probeRows.Count -eq 1 -and [int64]$probeRows[0].'FactSales Rows' -eq 121253) {
            $selectedConnection = $conn
            $selectedPort = $port
            break
        }

        $conn.Close()
    }
    catch {
        if ($conn -and $conn.State -eq 1) { $conn.Close() }
        continue
    }
}

if (-not $selectedConnection) {
    throw @"
Could not identify the open Retail360 Power BI model.
Make sure Retail360.pbip is open and the model has finished refreshing.
"@
}

Write-Host "Connected to Retail360 Power BI semantic model on localhost:$selectedPort" -ForegroundColor Green

$query = Get-Content $QueryPath -Raw
$recordset = $selectedConnection.Execute($query)
$rows = Recordset-ToObjects -Recordset $recordset
$recordset.Close()
$selectedConnection.Close()

if (-not $rows -or $rows.Count -eq 0) {
    throw "The Stage 5 DAX QA query returned no rows."
}

$proofDir = Split-Path -Parent $ProofCsvPath
New-Item -ItemType Directory -Force -Path $proofDir | Out-Null
$rows | Export-Csv -Path $ProofCsvPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host ("{0,-38} {1,20} {2,20} {3,8}" -f "Check","Actual","Expected","Status")
Write-Host ("-" * 92)

$failures = 0
foreach ($row in $rows) {
    $status = [string]$row.Status
    if ($status -ne "PASS") { $failures++ }

    $actual = [string]$row.Actual
    $expected = [string]$row.Expected
    Write-Host ("{0,-38} {1,20} {2,20} {3,8}" -f $row.Check,$actual,$expected,$status)
}

Write-Host ("-" * 92)
Write-Host "Runtime proof CSV: $ProofCsvPath"

if ($failures -gt 0) {
    throw "Stage 5 Power BI runtime QA FAILED: $failures check(s) failed."
}

Write-Host ""
Write-Host "STAGE 5 POWER BI RUNTIME QA PASSED: $($rows.Count)/$($rows.Count) checks." -ForegroundColor Green
Write-Host "Retail360 semantic model is loaded and queryable inside Power BI Desktop." -ForegroundColor Green
