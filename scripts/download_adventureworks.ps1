param(
    [switch]$IncludeFacts,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$BaseUrl = "https://raw.githubusercontent.com/microsoft/sql-server-samples/master/samples/databases/adventure-works/data-warehouse-install-script"
$OutputRoot = Join-Path $PSScriptRoot "..\data\raw\adventureworks"

$DimensionFiles = @(
    "DimCurrency.csv",
    "DimCustomer.csv",
    "DimDate.csv",
    "DimGeography.csv",
    "DimProduct.csv",
    "DimProductCategory.csv",
    "DimProductSubcategory.csv",
    "DimPromotion.csv",
    "DimReseller.csv",
    "DimSalesTerritory.csv"
)

$FactFiles = @(
    "FactInternetSales.csv",
    "FactResellerSales.csv",
    "FactProductInventory.csv"
)

$Files = @($DimensionFiles)
if ($IncludeFacts) {
    $Files += $FactFiles
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

Write-Host ""
Write-Host "Retail360 AdventureWorksDW downloader" -ForegroundColor Cyan
Write-Host "Destination: $OutputRoot"

foreach ($fileName in $Files) {
    $url = "$BaseUrl/$fileName"
    $destination = Join-Path $OutputRoot $fileName

    if ((Test-Path $destination) -and (-not $Force)) {
        $existing = Get-Item $destination
        if ($existing.Length -gt 0) {
            Write-Host "Already exists: $fileName ($($existing.Length) bytes)"
            continue
        }
    }

    Write-Host "Downloading: $fileName"

    try {
        Invoke-WebRequest -Uri $url -OutFile $destination -Headers @{ "User-Agent" = "Retail360-PowerBI-Analytics" }
        $downloaded = Get-Item $destination
        if ($downloaded.Length -eq 0) { throw "Downloaded file is empty." }
        Write-Host "OK: $fileName ($($downloaded.Length) bytes)" -ForegroundColor Green
    }
    catch {
        if (Test-Path $destination) { Remove-Item $destination -Force -ErrorAction SilentlyContinue }
        throw "Failed to download $fileName from $url. $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Download complete." -ForegroundColor Green
Write-Host "Files downloaded/available: $($Files.Count)"
Write-Host "Output: $((Resolve-Path $OutputRoot).Path)"

if (-not $IncludeFacts) {
    Write-Host ""
    Write-Host "Dimension phase complete." -ForegroundColor Yellow
    Write-Host "After validation, download facts with:"
    Write-Host ".\scripts\download_adventureworks.ps1 -IncludeFacts"
}
