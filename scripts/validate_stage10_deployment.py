from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "powerbi/Retail360.pbip",
    "docs/deployment/README.md",
    "docs/deployment/powerbi-refresh-deployment.md",
    "docs/deployment/pbip-pbix-strategy.md",
    "docs/deployment/powerbi-service-publish-checklist.md",
    "docs/deployment/stage10-deployment-summary.md",
    "docs/deployment/release-manifest.json",
    "scripts/package_stage10_release.ps1",
    "docs/recruiter/setup-guide.md",
]

SCREENSHOTS = [
    f"docs/screenshots/{i:02d}-{name}.png"
    for i, name in enumerate(
        [
            "executive-overview",
            "sales-growth",
            "product-profitability",
            "customer-analytics",
            "channel-reseller",
            "geography-territory",
            "promotion-analysis",
            "inventory-analytics",
            "drillthrough-detail",
            "model-data-quality",
        ],
        start=1,
    )
]


def fail(message: str) -> None:
    raise SystemExit(f"Stage 10 deployment validation FAILED: {message}")


def main() -> None:
    for rel in REQUIRED + SCREENSHOTS:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            fail(f"missing/empty deployment artifact: {rel}")

    manifest_path = ROOT / "docs/deployment/release-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid release manifest JSON: {exc}")

    expected = {
        "project": "Retail360",
        "release_version": "1.0.0-portfolio",
        "stage": 10,
        "stage_status": "complete-fallback-deployment",
        "deployment_mode": "portfolio-local-fallback",
        "canonical_artifact": "powerbi/Retail360.pbip",
        "refresh_mode": "Import",
        "power_bi_service_status": "optional-not-claimed",
        "validated_report_pages": 10,
        "hidden_tooltip_pages": 1,
        "governed_dax_measures": 78,
        "screenshots": 10,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            fail(f"release manifest mismatch for {key}: {manifest.get(key)!r}")

    summary = (ROOT / "docs/deployment/stage10-deployment-summary.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs/deployment/powerbi-service-publish-checklist.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/roadmap/end-to-end-build-plan.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts/package_stage10_release.ps1").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    required_summary_tokens = [
        "COMPLETE (portfolio/fallback deployment path)",
        "Power BI Service publication remains an optional environment step",
        "SHA-256",
        "dist/",
    ]
    for token in required_summary_tokens:
        if token not in summary:
            fail(f"Stage 10 summary missing token: {token}")

    for token in [
        "on-premises data gateway",
        "RLS",
        "109,809,274.2030",
        "does not claim that Service publication has occurred",
    ]:
        if token not in checklist:
            fail(f"Power BI Service checklist missing token: {token}")

    if "Status: COMPLETE — PORTFOLIO/FALLBACK DEPLOYMENT" not in roadmap:
        fail("roadmap does not mark Stage 10 fallback deployment complete")

    for token in [
        "Stage 10 deployment",
        "package_stage10_release.ps1",
        "Power BI Service ready",
        "portfolio/fallback deployment",
    ]:
        if token not in readme:
            fail(f"README missing Stage 10 token: {token}")

    for token in [
        "SHA256SUMS.txt",
        "Compress-Archive",
        ".pbi",
        ".runtime",
        "credentials",
        "secrets",
    ]:
        if token not in script:
            fail(f"release packaging helper missing safety token: {token}")

    if "dist/" not in gitignore:
        fail("generated dist/ release output must be ignored")

    if any(secret in (summary + checklist + script) for secret in [
        "Retail360BI2026",
        "Retail360_Local_2026",
    ]):
        fail("known local development credential leaked into Stage 10 assets")

    non_ascii = sorted({ch for ch in script if ord(ch) > 127})
    if non_ascii:
        cps = ", ".join(f"U+{ord(ch):04X}" for ch in non_ascii)
        fail(f"package_stage10_release.ps1 must remain ASCII-only for Windows PowerShell 5.1; found {cps}")

    print("Retail360 Stage 10 deployment contract")
    print("-" * 76)
    print("Canonical PBIP:           PASS")
    print("Deployment documentation: PASS")
    print("Service publish checklist:PASS")
    print("Release manifest:         PASS")
    print("Dashboard evidence:       10/10 PASS")
    print("Release packaging helper: PASS")
    print("Secret-exclusion policy:  PASS")
    print("Generated dist/ ignored:  PASS")
    print("Service claim boundary:   PASS")
    print("-" * 76)
    print("Stage 10 portfolio/fallback deployment validation PASSED.")


if __name__ == "__main__":
    main()
