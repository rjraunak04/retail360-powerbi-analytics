param(
    [string]$Version = "1.0.0-portfolio",
    [string]$OutputRoot = "dist"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ReleaseName = "Retail360-$Version"
$OutputRootPath = Join-Path $Root $OutputRoot
$ReleaseDir = Join-Path $OutputRootPath $ReleaseName
$ZipPath = Join-Path $OutputRootPath ($ReleaseName + ".zip")

function Copy-FilteredTree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Required release source is missing: $Source"
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    $sourceFull = (Resolve-Path $Source).Path.TrimEnd("\", "/")

    Get-ChildItem $Source -Recurse -File -Force | ForEach-Object {
        $full = $_.FullName
        $relative = $full.Substring($sourceFull.Length).TrimStart([char[]]"\/")

        if ($relative -match "(^|[\\/])\.pbi([\\/]|$)") { return }
        if ($relative -match "(^|[\\/])\.runtime([\\/]|$)") { return }
        if ($relative -match "(^|[\\/])__pycache__([\\/]|$)") { return }
        if ($relative -match "(^|[\\/])\.venv([\\/]|$)") { return }
        if ($_.Name -match "^\.env$") { return }
        if ($_.Name -match "^credentials\.") { return }
        if ($_.Name -match "^secrets\.") { return }
        if ($_.Name -match "\.localSettings\.json$") { return }
        if ($_.Name -match "\.pbix\.autosave$") { return }

        $target = Join-Path $Destination $relative
        $targetDir = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        Copy-Item $full $target -Force
    }
}

Write-Host "Retail360 Stage 10 release packaging" -ForegroundColor Cyan

if (Test-Path $ReleaseDir) {
    Remove-Item $ReleaseDir -Recurse -Force
}
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

foreach ($file in @("README.md", "compose.yml", "requirements.txt", ".env.example")) {
    $source = Join-Path $Root $file
    if (-not (Test-Path $source)) {
        throw "Required release file is missing: $file"
    }
    Copy-Item $source (Join-Path $ReleaseDir $file) -Force
}

foreach ($dir in @("powerbi", "power-query", "scripts", "sql", "docs")) {
    Copy-FilteredTree -Source (Join-Path $Root $dir) -Destination (Join-Path $ReleaseDir $dir)
}

$workflowSource = Join-Path (Join-Path $Root ".github") "workflows"
if (Test-Path $workflowSource) {
    $workflowDestination = Join-Path (Join-Path $ReleaseDir ".github") "workflows"
    Copy-FilteredTree -Source $workflowSource -Destination $workflowDestination
}

$commit = "unknown"
try {
    $commit = (git rev-parse HEAD 2>$null).Trim()
}
catch {}

$releaseInfo = @(
    "Retail360 portfolio release",
    "Version: $Version",
    "Generated UTC: $([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))",
    "Git commit: $commit",
    "Canonical Power BI artifact: powerbi/Retail360.pbip",
    "Power BI Service publication: optional / not claimed by repository"
)
$releaseInfo | Set-Content (Join-Path $ReleaseDir "RELEASE_INFO.txt") -Encoding UTF8

$checksumPath = Join-Path $ReleaseDir "SHA256SUMS.txt"
$hashLines = Get-ChildItem $ReleaseDir -Recurse -File |
    Where-Object { $_.FullName -ne $checksumPath } |
    Sort-Object FullName |
    ForEach-Object {
        $relative = $_.FullName.Substring($ReleaseDir.Length).TrimStart([char[]]"\/").Replace("\", "/")
        $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $relative"
    }
$hashLines | Set-Content $checksumPath -Encoding ASCII

Compress-Archive -Path (Join-Path $ReleaseDir "*") -DestinationPath $ZipPath -CompressionLevel Optimal

Write-Host ""
Write-Host "STAGE 10 PORTFOLIO RELEASE PACKAGE CREATED." -ForegroundColor Green
Write-Host "Folder: $ReleaseDir" -ForegroundColor Green
Write-Host "Archive: $ZipPath" -ForegroundColor Green
Write-Host "Checksums: $checksumPath" -ForegroundColor Green
