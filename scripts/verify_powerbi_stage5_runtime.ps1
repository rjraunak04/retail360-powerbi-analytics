param(
    [int]$StartupTimeoutSeconds = 120,
    [int]$ModelProbeTimeoutSeconds = 30,
    [string]$QueryPath = "",
    [string]$ProofCsvPath = "",
    [string]$StageLabel = "Stage 5"
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
            $name = [string]$field.Name
            if ($name.StartsWith("[") -and $name.EndsWith("]")) {
                $name = $name.Substring(1, $name.Length - 2)
            }
            $row[$name] = $field.Value
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
    $conn.ConnectionTimeout = 2

    $connectionString = "Provider=MSOLAP;Data Source=localhost:$Port;Integrated Security=SSPI;"
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
        # adSchemaCatalogs = 1. OpenSchema is more compatible across MSOLAP
        # provider versions than issuing a DMV query before selecting a catalog.
        $rs = $conn.OpenSchema(1)
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

    # Last-resort discovery: modern Power BI Desktop builds can hide the
    # Analysis Services workspace path from the parent process command line.
    # Scan all local listening TCP ports and let the MSOLAP handshake identify
    # the Analysis Services endpoint. This is safe because we only connect to
    # loopback listeners and use a very short timeout.
    if ($ports.Count -eq 0) {
        Write-Host "No engine port found from process/workspace metadata; scanning local listeners..." -ForegroundColor Yellow
        try {
            $listeners = Get-NetTCPConnection -State Listen -ErrorAction Stop |
                Where-Object {
                    $_.LocalPort -gt 1024 -and (
                        $_.LocalAddress -eq '127.0.0.1' -or
                        $_.LocalAddress -eq '::1' -or
                        $_.LocalAddress -eq '0.0.0.0' -or
                        $_.LocalAddress -eq '::'
                    )
                }
            foreach ($listener in $listeners) {
                [void]$ports.Add([int]$listener.LocalPort)
            }
        }
        catch {
            $netstat = netstat -ano -p tcp
            foreach ($line in $netstat) {
                if ($line -notmatch "LISTENING") { continue }
                $parts = ($line -replace '^\s+', '') -split '\s+'
                if ($parts.Count -lt 5) { continue }
                $local = $parts[1]
                $portText = ($local -split ':')[-1]
                $port = 0
                if ([int]::TryParse($portText, [ref]$port) -and $port -gt 1024) {
                    [void]$ports.Add($port)
                }
            }
        }
    }

    return @($ports | Sort-Object -Unique)
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
$query = Get-Content $QueryPath -Raw
$probeDeadline = (Get-Date).AddSeconds($ModelProbeTimeoutSeconds)
$runtimeRows = $null
$selectedPort = $null
$selectedDatabase = $null
$lastProbeError = $null
$reportedCandidates = New-Object System.Collections.Generic.HashSet[string]

while ((Get-Date) -lt $probeDeadline -and -not $runtimeRows) {
    $ports = Get-MsmdsrvPorts
    if ($reportedCandidates.Add("ports:" + (($ports | Sort-Object) -join ","))) {
        Write-Host ("Candidate local ports: " + $ports.Count + " -> " + (($ports | Sort-Object) -join ", ")) -ForegroundColor DarkGray
    }

    foreach ($port in $ports) {
        try {
            $catalogs = Get-AnalysisServicesCatalogs -Port $port
            if (-not $catalogs -or $catalogs.Count -eq 0) {
                $lastProbeError = "Port $port responded but returned no Analysis Services catalogs."
                continue
            }
            if ($reportedCandidates.Add("catalogs:" + $port + ":" + ($catalogs -join ","))) {
                Write-Host ("Port " + $port + " catalogs: " + ($catalogs -join ", ")) -ForegroundColor DarkGray
            }
        }
        catch {
            $lastProbeError = "Port $port catalog discovery: $($_.Exception.Message)"
            continue
        }

        foreach ($catalog in $catalogs) {
            $conn = $null
            try {
                $conn = Open-AdodbConnection -Port $port -Database $catalog

                # Execute the real Stage 5 proof directly. This is both model
                # identification and runtime validation, avoiding provider-
                # specific assumptions about probe column names.
                $recordset = $conn.Execute($query)
                $candidateRows = Recordset-ToObjects -Recordset $recordset
                $recordset.Close()
                $conn.Close()

                if (-not $candidateRows -or $candidateRows.Count -eq 0) {
                    $lastProbeError = "Port $port catalog ${catalog} returned no Stage 5 QA rows."
                    continue
                }

                $candidateFailures = @($candidateRows | Where-Object { [string]$_.Status -ne "PASS" })
                $checkNames = @($candidateRows | ForEach-Object { [string]$_.Check })

                if (
                    $candidateRows.Count -eq 20 -and
                    $candidateFailures.Count -eq 0 -and
                    $checkNames -contains "Total Sales"
                ) {
                    $runtimeRows = $candidateRows
                    $selectedPort = $port
                    $selectedDatabase = $catalog
                    break
                }

                $lastProbeError = "Port $port catalog ${catalog} ran Stage 5 QA but returned $($candidateRows.Count) row(s) with $($candidateFailures.Count) failure(s)."
            }
            catch {
                $lastProbeError = "Port $port catalog ${catalog}: $($_.Exception.Message)"
                if ($conn -and $conn.State -eq 1) {
                    try { $conn.Close() } catch {}
                }
            }
        }

        if ($runtimeRows) { break }
    }

    if (-not $runtimeRows) {
        Start-Sleep -Seconds 3
    }
}

if (-not $runtimeRows) {
    $details = if ($lastProbeError) { " Last probe error: $lastProbeError" } else { "" }
    throw "Could not connect to the open Retail360 semantic model within $ModelProbeTimeoutSeconds seconds.$details If the error mentions MSOLAP, repair/update Power BI Desktop so its Analysis Services OLE DB provider is registered."
}

Write-Host "Connected to Retail360 Power BI semantic model on localhost:$selectedPort" -ForegroundColor Green
Write-Host "Power BI model database: $selectedDatabase" -ForegroundColor DarkGray

$rows = $runtimeRows

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
Write-Host "$($StageLabel.ToUpper()) POWER BI RUNTIME QA PASSED: $($rows.Count)/$($rows.Count) checks." -ForegroundColor Green
Write-Host "Retail360 semantic model is loaded and queryable inside Power BI Desktop." -ForegroundColor Green
