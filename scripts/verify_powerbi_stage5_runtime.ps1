param(
    [int]$StartupTimeoutSeconds = 120,
    [int]$ModelProbeTimeoutSeconds = 120,
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
$Project = Join-Path $Root "powerbi\Retail360.pbip"

if (-not (Test-Path $Project)) {
    throw "Retail360 PBIP project not found: $Project"
}
if (-not (Test-Path $QueryPath)) {
    throw "Stage 5 DAX QA query not found: $QueryPath"
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

function Open-AdodbConnection {
    param(
        [int]$Port,
        [string]$Database = ""
    )

    $conn = New-Object -ComObject ADODB.Connection
    $conn.CommandTimeout = 120
    $conn.ConnectionTimeout = 10

    $connectionString = "Provider=MSOLAP;Data Source=127.0.0.1:$Port;Integrated Security=SSPI;"
    if ($Database) {
        $connectionString += "Initial Catalog=$Database;"
    }

    $conn.Open($connectionString)
    return $conn
}

function Get-AnalysisServicesCatalogs {
    param(
        [int]$Port
    )

    $conn = $null
    try {
        $conn = Open-AdodbConnection -Port $Port
        $rs = $conn.Execute('SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS')
        $catalogs = New-Object System.Collections.Generic.List[string]

        while (-not $rs.EOF) {
            $name = [string]$rs.Fields.Item("CATALOG_NAME").Value
            if ($name) {
                $catalogs.Add($name)
            }
            $rs.MoveNext()
        }

        $rs.Close()
        $conn.Close()
        return @($catalogs)
    }
    catch {
        if ($conn -and $conn.State -eq 1) {
            try { $conn.Close() } catch {}
        }
        throw
    }
}

function Get-MsmdsrvPorts {
    $ports = New-Object System.Collections.Generic.HashSet[int]

    $processes = Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue
    foreach ($proc in @($processes)) {
        try {
            $connections = Get-NetTCPConnection -State Listen -OwningProcess $proc.ProcessId -ErrorAction SilentlyContinue
            foreach ($c in @($connections)) {
                if ($c.LocalPort -gt 0) {
                    [void]$ports.Add([int]$c.LocalPort)
                }
            }
        }
        catch {
            # Fall back to workspace port files below.
        }

        if ($proc.CommandLine) {
            $match = [regex]::Match($proc.CommandLine, '-s\s+"([^"]+)"')
            if (-not $match.Success) {
                $match = [regex]::Match($proc.CommandLine, '-s\s+([^\s]+)')
            }

            if ($match.Success) {
                $workspace = $match.Groups[1].Value.Trim('"')
                foreach ($portFile in @(
                    (Join-Path $workspace "msmdsrv.port.txt"),
                    (Join-Path $workspace "Data\msmdsrv.port.txt")
                )) {
                    if (Test-Path $portFile) {
                        try {
                            $raw = (Get-Content $portFile -Raw).Trim([char]0).Trim()
                            if ($raw -match '^\d+$') {
                                [void]$ports.Add([int]$raw)
                            }
                            else {
                                $bytes = [System.IO.File]::ReadAllBytes($portFile)
                                $unicode = [System.Text.Encoding]::Unicode.GetString($bytes).Trim([char]0).Trim()
                                if ($unicode -match '^\d+$') {
                                    [void]$ports.Add([int]$unicode)
                                }
                            }
                        }
                        catch {}
                    }
                }
            }
        }
    }

    # Modern Power BI Desktop / Store builds can place workspaces under either
    # of these folders. Use them as an additional discovery fallback.
    foreach ($rootCandidate in @(
        (Join-Path $env:LOCALAPPDATA "Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces")
    )) {
        if (Test-Path $rootCandidate) {
            Get-ChildItem $rootCandidate -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                foreach ($portFile in @(
                    (Join-Path $_.FullName "msmdsrv.port.txt"),
                    (Join-Path $_.FullName "Data\msmdsrv.port.txt")
                )) {
                    if (Test-Path $portFile) {
                        try {
                            $raw = (Get-Content $portFile -Raw).Trim([char]0).Trim()
                            if ($raw -match '^\d+$') {
                                [void]$ports.Add([int]$raw)
                            }
                        }
                        catch {}
                    }
                }
            }
        }
    }

    # netstat fallback: Power BI Desktop's local Analysis Services engine listens
    # on a dynamically assigned TCP port. Microsoft documents netstat as a
    # supported way to discover that port.
    try {
        $pids = @(
            Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue |
                ForEach-Object { [int]$_.ProcessId }
        )

        if ($pids.Count -gt 0) {
            $netstat = netstat -ano -p tcp
            foreach ($line in $netstat) {
                if ($line -notmatch "LISTENING") { continue }

                $parts = ($line -replace '^\s+', '') -split '\s+'
                if ($parts.Count -lt 5) { continue }

                $pid = 0
                if (-not [int]::TryParse($parts[4], [ref]$pid)) { continue }
                if ($pids -notcontains $pid) { continue }

                $local = $parts[1]
                $portText = ($local -split ':')[-1]
                $port = 0
                if ([int]::TryParse($portText, [ref]$port) -and $port -gt 0) {
                    [void]$ports.Add($port)
                }
            }
        }
    }
    catch {}

    return @($ports)
}

function Ensure-PowerBIModelRunning {
    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)

    if (-not (Get-Process PBIDesktop -ErrorAction SilentlyContinue)) {
        Write-Host "Power BI Desktop is not open. Starting Retail360.pbip..." -ForegroundColor Yellow
        Start-Process $Project
    }
    else {
        Write-Host "Power BI Desktop is already running." -ForegroundColor DarkGray

        if (-not (Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue)) {
            Write-Host "No semantic-model engine found yet. Opening Retail360.pbip..." -ForegroundColor Yellow
            Start-Process $Project
        }
    }

    Write-Host "Waiting for the Power BI semantic-model engine..." -ForegroundColor DarkGray
    while ((Get-Date) -lt $deadline) {
        $engine = Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction SilentlyContinue
        if ($engine) {
            Start-Sleep -Seconds 3
            return
        }
        Start-Sleep -Seconds 2
    }

    throw "Power BI Desktop opened but its semantic-model engine did not start within $StartupTimeoutSeconds seconds."
}

Write-Host "Retail360 Stage 5 Power BI runtime verifier" -ForegroundColor Cyan
Write-Host ("Project: " + $Project) -ForegroundColor DarkGray

# PostgreSQL must remain reachable because Power BI may refresh on open.
try {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        docker compose up -d postgres | Out-Host
    }
}
catch {
    Write-Host "Docker check skipped/failed; continuing because the Power BI model may already be loaded." -ForegroundColor Yellow
}

Ensure-PowerBIModelRunning

Write-Host "Searching for the Retail360 Power BI semantic model..." -ForegroundColor DarkGray
$probeDeadline = (Get-Date).AddSeconds($ModelProbeTimeoutSeconds)
$selectedConnection = $null
$selectedPort = $null
$selectedDatabase = $null
$lastProbeError = $null

while ((Get-Date) -lt $probeDeadline -and -not $selectedConnection) {
    $ports = Get-MsmdsrvPorts

    foreach ($port in $ports) {
        try {
            $catalogs = Get-AnalysisServicesCatalogs -Port $port
        }
        catch {
            $lastProbeError = "Port $port catalog discovery: $($_.Exception.Message)"
            continue
        }

        foreach ($catalog in $catalogs) {
            $conn = $null
            try {
                $conn = Open-AdodbConnection -Port $port -Database $catalog
                $probe = $conn.Execute('EVALUATE ROW("FactSales Rows", COUNTROWS(FactSales), "DimDate Rows", COUNTROWS(DimDate))')
                $probeRows = Recordset-ToObjects -Recordset $probe
                $probe.Close()

                if (
                    $probeRows.Count -eq 1 -and
                    [int64]$probeRows[0].'FactSales Rows' -eq 121253 -and
                    [int64]$probeRows[0].'DimDate Rows' -eq 3652
                ) {
                    $selectedConnection = $conn
                    $selectedPort = $port
                    $selectedDatabase = $catalog
                    break
                }

                $conn.Close()
            }
            catch {
                $lastProbeError = "Port $port catalog ${catalog}: $($_.Exception.Message)"
                if ($conn -and $conn.State -eq 1) {
                    try { $conn.Close() } catch {}
                }
            }
        }

        if ($selectedConnection) { break }
    }

    if (-not $selectedConnection) {
        Start-Sleep -Seconds 3
    }
}

if (-not $selectedConnection) {
    $details = if ($lastProbeError) { " Last probe error: $lastProbeError" } else { "" }
    throw "Could not connect to the open Retail360 semantic model within $ModelProbeTimeoutSeconds seconds.$details"
}

Write-Host "Connected to Retail360 Power BI semantic model on 127.0.0.1:$selectedPort" -ForegroundColor Green
Write-Host "Power BI model database: $selectedDatabase" -ForegroundColor DarkGray

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
