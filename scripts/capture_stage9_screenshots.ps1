param(
    [int]$DelaySeconds = 3,
    [switch]$CommitAndPush
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$OutputDir = Join-Path $Root "docs\screenshots"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

if (-not ("Retail360.NativeWindow" -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;

namespace Retail360 {
    public static class NativeWindow {
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }

        [DllImport("user32.dll")]
        public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    }
}
"@
}

$processes = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 })

if ($processes.Count -ne 1) {
    throw "Expected exactly one visible Power BI Desktop window; found $($processes.Count). Close extra windows and keep only Retail360 open."
}

$proc = $processes[0]
$hwnd = $proc.MainWindowHandle

[Retail360.NativeWindow]::ShowWindow($hwnd, 3) | Out-Null
[Retail360.NativeWindow]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Seconds 2

for ($i = 0; $i -lt 15; $i++) {
    [System.Windows.Forms.SendKeys]::SendWait("^{PGUP}")
    Start-Sleep -Milliseconds 120
}
Start-Sleep -Seconds $DelaySeconds

$pages = @(
    @{ File = "01-executive-overview.png"; Name = "Executive Overview" },
    @{ File = "02-sales-growth.png"; Name = "Sales & Growth" },
    @{ File = "03-product-profitability.png"; Name = "Product & Profitability" },
    @{ File = "04-customer-analytics.png"; Name = "Customer Analytics" },
    @{ File = "05-channel-reseller.png"; Name = "Channel / Reseller Analytics" },
    @{ File = "06-geography-territory.png"; Name = "Geography & Territory" },
    @{ File = "07-promotion-analysis.png"; Name = "Promotion Analysis" },
    @{ File = "08-inventory-analytics.png"; Name = "Inventory Analytics" },
    @{ File = "09-drillthrough-detail.png"; Name = "Drill-through Detail" },
    @{ File = "10-model-data-quality.png"; Name = "Model / Data Quality" }
)

function Save-PowerBIWindowScreenshot {
    param(
        [IntPtr]$WindowHandle,
        [string]$Path
    )

    $rect = New-Object Retail360.NativeWindow+RECT
    if (-not [Retail360.NativeWindow]::GetWindowRect($WindowHandle, [ref]$rect)) {
        throw "Could not read the Power BI window bounds."
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    if ($width -lt 1000 -or $height -lt 600) {
        throw "Power BI window is too small for recruiter screenshots: ${width}x${height}."
    }

    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

    try {
        $graphics.CopyFromScreen(
            (New-Object System.Drawing.Point($rect.Left, $rect.Top)),
            [System.Drawing.Point]::Empty,
            (New-Object System.Drawing.Size($width, $height))
        )
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

for ($i = 0; $i -lt $pages.Count; $i++) {
    [Retail360.NativeWindow]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500

    $target = Join-Path $OutputDir $pages[$i].File
    Write-Host ("Capturing " + ($i + 1) + "/10 - " + $pages[$i].Name) -ForegroundColor Cyan
    Save-PowerBIWindowScreenshot -WindowHandle $hwnd -Path $target

    $info = Get-Item $target
    if ($info.Length -lt 50000) {
        throw "Screenshot looks unexpectedly small: $target ($($info.Length) bytes)"
    }

    if ($i -lt ($pages.Count - 1)) {
        [System.Windows.Forms.SendKeys]::SendWait("^{PGDN}")
        Start-Sleep -Seconds $DelaySeconds
    }
}

Write-Host ""
Write-Host "Stage 9 screenshots captured successfully: 10/10" -ForegroundColor Green
Write-Host "Output: $OutputDir" -ForegroundColor Green

python scripts/validate_stage9_packaging.py --require-screenshots
if ($LASTEXITCODE -ne 0) {
    throw "Stage 9 screenshot validation failed."
}

if ($CommitAndPush) {
    $roadmapPath = Join-Path $Root "docs\roadmap\end-to-end-build-plan.md"
    if (Test-Path $roadmapPath) {
        $roadmap = Get-Content $roadmapPath -Raw
        $stage9Pattern = '(?ms)(## Stage 9[^\r\n]*GitHub and Recruiter Packaging\r?\n)Status: REPOSITORY COMPLETE[^\r\n]*RENDERED SCREENSHOT CAPTURE PENDING'
        $roadmap = [regex]::Replace($roadmap, $stage9Pattern, '${1}Status: COMPLETE')
        Set-Content -Path $roadmapPath -Value $roadmap -Encoding UTF8
    }

    $summaryPath = Join-Path $Root "docs\recruiter\stage9-validation-summary.md"
    if (Test-Path $summaryPath) {
        $summary = Get-Content $summaryPath -Raw
        if ($summary -notmatch "Final screenshot evidence") {
            $append = @"

## Final screenshot evidence

Status: PASSED

The automated local Power BI Desktop capture produced and validated all 10/10 real rendered report screenshots under docs/screenshots/.

Final local gate:
- 10/10 report screenshots present
- each screenshot passed the minimum file-size sanity check
- Stage 9 packaging validation with --require-screenshots passed

### Stage 9 decision

Stage 9 - GitHub and Recruiter Packaging: COMPLETE
"@
            $summary = $summary + $append
            Set-Content -Path $summaryPath -Value $summary -Encoding UTF8
        }
    }

    python scripts/validate_stage9_packaging.py --require-screenshots
    if ($LASTEXITCODE -ne 0) {
        throw "Final Stage 9 packaging validation failed after status update."
    }

    $currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
    if (-not $currentBranch -or $currentBranch -eq "HEAD") {
        throw "Cannot commit screenshots from a detached HEAD."
    }

    git add docs/screenshots/*.png docs/roadmap/end-to-end-build-plan.md docs/recruiter/stage9-validation-summary.md
    git status --short

    $staged = git diff --cached --name-only
    if ($staged) {
        git commit -m "docs: finalize Retail360 Stage 9 recruiter package"
        if ($LASTEXITCODE -ne 0) { throw "Git commit failed." }

        git push origin $currentBranch
        if ($LASTEXITCODE -ne 0) { throw "Git push failed." }

        Write-Host "Stage 9 screenshots/status committed and pushed to $currentBranch." -ForegroundColor Green
    }
    else {
        Write-Host "No new Stage 9 changes to commit." -ForegroundColor DarkGray
    }
}
