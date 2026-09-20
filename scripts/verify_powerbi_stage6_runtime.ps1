param(
    [switch]$CleanRestart
)

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


function Test-DockerEngine {
    # Windows PowerShell turns native stderr into ErrorRecord objects when
    # ErrorActionPreference=Stop. Docker can emit harmless CLI-plugin warnings
    # (for example a broken docker-agent plugin) even when the engine is healthy.
    # Run the probe through cmd.exe and suppress both streams, then trust the
    # native exit code instead of stderr text.
    & $env:ComSpec /d /s /c "docker info >nul 2>nul"
    return ($LASTEXITCODE -eq 0)
}

function Invoke-DockerComposeUp {
    $output = & $env:ComSpec /d /s /c "docker compose up -d postgres 2>&1"
    $exitCode = $LASTEXITCODE
    if ($output) { $output | Out-Host }
    if ($exitCode -ne 0) {
        throw "Could not start the Retail360 PostgreSQL container. Docker exit code: $exitCode"
    }
}

function Test-PostgresContainerReady {
    param([string]$User)
    & $env:ComSpec /d /s /c "docker compose exec -T postgres pg_isready -U $User >nul 2>nul"
    return ($LASTEXITCODE -eq 0)
}

Write-Host "Retail360 Stage 6 full validation gate" -ForegroundColor Cyan

Write-Host "Starting/checking PostgreSQL..." -ForegroundColor DarkGray
if (-not (Test-DockerEngine)) {
    $DockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $DockerDesktop) {
        Write-Host "Docker Desktop is not running; starting it automatically..." -ForegroundColor Yellow
        Start-Process $DockerDesktop
        $dockerReady = $false
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Seconds 2
            if (Test-DockerEngine) {
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

Invoke-DockerComposeUp

$PgUser = if ($env:PGUSER) { $env:PGUSER } else { "postgres" }
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    if (Test-PostgresContainerReady -User $PgUser) {
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


function Invoke-CleanPowerBIRestart {
    param(
        [string]$ProjectPath
    )

    Write-Host "Preparing a clean Power BI Desktop runtime..." -ForegroundColor DarkGray

    $desktopProcesses = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue)
    if ($desktopProcesses.Count -gt 0) {
        Write-Host ("Power BI Desktop instance(s) detected: " + $desktopProcesses.Count) -ForegroundColor Yellow
        Write-Host "Requesting a graceful close so stale semantic-model state and memory are released..." -ForegroundColor Yellow

        foreach ($proc in $desktopProcesses) {
            try { [void]$proc.CloseMainWindow() } catch {}
        }

        $closeDeadline = (Get-Date).AddSeconds(30)
        do {
            Start-Sleep -Seconds 2
            $desktopProcesses = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue)
        } while ($desktopProcesses.Count -gt 0 -and (Get-Date) -lt $closeDeadline)

        if ($desktopProcesses.Count -gt 0) {
            throw "Power BI Desktop is still open. Save/close any Power BI window or Save dialog, then rerun this verifier. The verifier will not force-kill Desktop because that could discard unsaved work."
        }
    }

    # With Desktop closed, any remaining local Analysis Services process is
    # orphaned. Clearing these prevents memory pressure and stale catalog reuse.
    $orphanEngines = @(Get-Process msmdsrv -ErrorAction SilentlyContinue)
    foreach ($engine in $orphanEngines) {
        try {
            Write-Host ("Stopping orphan Analysis Services engine PID " + $engine.Id) -ForegroundColor Yellow
            Stop-Process -Id $engine.Id -Force -ErrorAction Stop
        }
        catch {}
    }

    # Remove only repository-local Power BI caches. These are ignored by Git.
    Get-ChildItem (Join-Path $Root "powerbi") -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq ".pbi" } |
        Sort-Object FullName -Descending |
        ForEach-Object {
            try {
                Write-Host ("Removing repository-local Power BI cache: " + $_.FullName) -ForegroundColor DarkGray
                Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
            }
            catch {}
        }

    # Remove stale verifier scratch state.
    if (Test-Path $RuntimeRoot) {
        Get-ChildItem $RuntimeRoot -Force -ErrorAction SilentlyContinue |
            ForEach-Object {
                try { Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop } catch {}
            }
    }

    # Memory preflight.
    #
    # The previous verifier used a hard 2 GB free-physical-RAM gate. That was a
    # conservative diagnostic guard, not a Power BI requirement, and on an
    # 8-GB-class Windows machine it could block forever even when Windows had
    # enough virtual-memory/pagefile headroom to load this ~922k-row model.
    #
    # First reclaim disposable WSL/Linux page cache (best effort) without
    # stopping Docker/PostgreSQL, then gate only on genuinely dangerous memory
    # pressure: <0.50 GB free physical RAM or <2 GB free virtual memory.
    try {
        Write-Host "Reclaiming disposable Docker/WSL cache before Power BI launch..." -ForegroundColor DarkGray
        & wsl.exe -d docker-desktop -u root sh -lc "sync; echo 3 > /proc/sys/vm/drop_caches" *> $null
        Start-Sleep -Seconds 2
    }
    catch {
        # Some Docker Desktop versions do not expose a docker-desktop distro.
        # Cache reclamation is optional; continue with the Windows memory check.
    }

    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $freePhysicalGb = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
        $freeVirtualGb = [math]::Round(($os.FreeVirtualMemory * 1KB) / 1GB, 2)

        Write-Host ("Free physical memory before Power BI launch: " + $freePhysicalGb + " GB") -ForegroundColor DarkGray
        Write-Host ("Free virtual memory before Power BI launch:  " + $freeVirtualGb + " GB") -ForegroundColor DarkGray

        if ($freePhysicalGb -lt 0.50) {
            throw "Only $freePhysicalGb GB physical RAM is free. Close one memory-heavy application and rerun Stage 6 verification."
        }
        if ($freeVirtualGb -lt 2.0) {
            throw "Only $freeVirtualGb GB virtual memory is free. Increase/enable the Windows pagefile or close a memory-heavy application, then rerun Stage 6 verification."
        }

        if ($freePhysicalGb -lt 1.50) {
            Write-Host "Low-memory mode: continuing because virtual-memory headroom is sufficient." -ForegroundColor Yellow
            Write-Host "Largest current processes (informational only):" -ForegroundColor Yellow
            Get-Process -ErrorAction SilentlyContinue |
                Sort-Object WorkingSet64 -Descending |
                Select-Object -First 8 Name, Id, @{Name="RAM_GB";Expression={[math]::Round($_.WorkingSet64 / 1GB, 2)}} |
                Format-Table -AutoSize | Out-Host
        }
    }
    catch {
        if (
            $_.Exception.Message -like "Only * physical RAM is free*" -or
            $_.Exception.Message -like "Only * virtual memory is free*"
        ) {
            throw
        }
        Write-Host "Memory preflight unavailable; continuing." -ForegroundColor Yellow
    }

    Write-Host "Opening canonical Retail360.pbip in a clean Power BI Desktop process..." -ForegroundColor Yellow
    Start-Process $ProjectPath
    Start-Sleep -Seconds 12
}


Write-Host "Preparing single-instance Power BI runtime..." -ForegroundColor DarkGray
Write-Host "Default mode reuses one already-open Retail360 model; use -CleanRestart only when a cold restart is specifically required." -ForegroundColor DarkGray

$RuntimeRoot = Join-Path $Root ".runtime"
New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

# Earlier Stage 6 verifier versions opened a second temporary PBIP instance on
# every run. Repeated retries could leave multiple Power BI/Analysis Services
# engines alive at once, increasing memory pressure and causing provider
# OutOfMemory/container-exit errors. Only orphaned temporary runtime instances
# are closed here; the user's canonical Retail360 window is left untouched.
$orphanRuntimeProcesses = @(
    Get-CimInstance Win32_Process -Filter "Name='PBIDesktop.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match '\\.runtime\\stage6-powerbi-'
        }
)
foreach ($proc in $orphanRuntimeProcesses) {
    try {
        Write-Host ("Closing orphan Stage 6 runtime Power BI process PID " + $proc.ProcessId) -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
    }
    catch {}
}

# Remove stale temporary project copies after their processes are gone.
Get-ChildItem $RuntimeRoot -Directory -Filter "stage6-powerbi-*" -ErrorAction SilentlyContinue |
    ForEach-Object {
        try { Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop } catch {}
    }

$CanonicalProject = Join-Path $Root "powerbi\Retail360.pbip"
$PowerBIProcess = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue)

if ($PowerBIProcess.Count -gt 1) {
    throw "Multiple Power BI Desktop instances are running ($($PowerBIProcess.Count)). Close extra Power BI windows and rerun. Stage 6 verification requires exactly one semantic-model engine."
}

if ($CleanRestart) {
    Invoke-CleanPowerBIRestart -ProjectPath $CanonicalProject
}
elseif ($PowerBIProcess.Count -eq 1) {
    Write-Host "Using the single already-open Retail360 Power BI Desktop instance for live Stage 6 QA." -ForegroundColor Green
}
else {
    Write-Host "Power BI Desktop is not running; opening canonical Retail360.pbip..." -ForegroundColor Yellow

    # Cold-start cache cleanup is safe only when Desktop is already closed.
    Get-ChildItem (Join-Path $Root "powerbi") -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq ".pbi" } |
        Sort-Object FullName -Descending |
        ForEach-Object {
            try { Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop } catch {}
        }

    Start-Process $CanonicalProject
    Start-Sleep -Seconds 12
}

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
