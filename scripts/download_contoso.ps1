param(
    [switch]$IncludeFacts
)

$ErrorActionPreference = "Stop"

$BaseUrl = "https://contosoretaildw.blob.core.windows.net/contosoretaildw-tables"
$OutputRoot = Join-Path $PSScriptRoot "..\data\raw\contoso"

$DimensionPrefixes = @(
    "DimChannel",
    "DimCurrency",
    "DimCustomer",
    "DimDate",
    "DimGeography",
    "DimProduct",
    "DimProductCategory",
    "DimProductSubcategory",
    "DimPromotion",
    "DimStore"
)

$FactPrefixes = @(
    "FactSales",
    "FactOnlineSales",
    "FactInventory"
)

$Prefixes = @($DimensionPrefixes)
if ($IncludeFacts) {
    $Prefixes += $FactPrefixes
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

function Get-BlobNames {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prefix
    )

    $marker = ""
    $names = @()

    do {
        $encodedPrefix = [System.Uri]::EscapeDataString("$Prefix/")
        $uri = "$BaseUrl?restype=container&comp=list&prefix=$encodedPrefix"

        if ($marker) {
            $encodedMarker = [System.Uri]::EscapeDataString($marker)
            $uri += "&marker=$encodedMarker"
        }

        $response = Invoke-RestMethod -Uri $uri -Method Get

        if ($response.EnumerationResults.Blobs.Blob) {
            $names += @(
                $response.EnumerationResults.Blobs.Blob |
                ForEach-Object { $_.Name }
            )
        }

        $marker = [string]$response.EnumerationResults.NextMarker
    }
    while ($marker)

    return $names
}

foreach ($prefix in $Prefixes) {
    Write-Host ""
    Write-Host "Discovering $prefix ..." -ForegroundColor Cyan

    $blobNames = @(Get-BlobNames -Prefix $prefix)

    if ($blobNames.Count -eq 0) {
        Write-Warning "No blobs found for $prefix"
        continue
    }

    foreach ($blobName in $blobNames) {
        $relativePath = $blobName.Replace("/", "\")
        $destination = Join-Path $OutputRoot $relativePath
        $destinationDirectory = Split-Path $destination -Parent

        New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null

        if (Test-Path $destination) {
            Write-Host "Already exists: $relativePath"
            continue
        }

        $escapedBlobPath = ($blobName.Split("/") |
            ForEach-Object { [System.Uri]::EscapeDataString($_) }) -join "/"

        $downloadUrl = "$BaseUrl/$escapedBlobPath"

        Write-Host "Downloading: $relativePath"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $destination
    }
}

Write-Host ""
Write-Host "Download complete." -ForegroundColor Green
Write-Host "Output: $((Resolve-Path $OutputRoot).Path)"

if (-not $IncludeFacts) {
    Write-Host ""
    Write-Host "Only dimension tables were downloaded."
    Write-Host "After validating them, run:" -ForegroundColor Yellow
    Write-Host ".\scripts\download_contoso.ps1 -IncludeFacts"
}
