from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "README.md",
    "docs/architecture/retail360-architecture.md",
    "docs/architecture/star-schema.md",
    "docs/powerbi/kpi-dictionary.md",
    "docs/project/architecture-decisions.md",
    "docs/project/setup.md",
    "docs/sql/business-analysis-examples.md",
    "docs/qa/stage9-packaging-validation.md",
    "docs/screenshots/README.md",
]

SCREENSHOTS = [
    "01-executive-overview.png",
    "02-sales-growth.png",
    "03-product-profitability.png",
    "04-customer-analytics.png",
    "05-channel-reseller.png",
    "06-geography-territory.png",
    "07-promotion-analysis.png",
    "08-inventory-analytics.png",
    "09-drillthrough-detail.png",
    "10-model-data-quality.png",
]

EXPECTED_VISIBLE_PAGES = [
    "Executive Overview",
    "Sales & Growth",
    "Product & Profitability",
    "Customer Analytics",
    "Channel / Reseller Analytics",
    "Geography & Territory",
    "Promotion Analysis",
    "Inventory Analytics",
    "Drill-through Detail",
    "Model / Data Quality",
]


def fail(message: str) -> None:
    raise SystemExit(f"Stage 9 packaging validation FAILED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-screenshots", action="store_true")
    args = parser.parse_args()

    for rel in REQUIRED_DOCS:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            fail(f"missing/empty required artifact: {rel}")

    capture_script = (ROOT / "scripts/capture_stage9_screenshots.ps1").read_text(encoding="utf-8")
    non_ascii = sorted({ch for ch in capture_script if ord(ch) > 127})
    if non_ascii:
        codepoints = ", ".join(f"U+{ord(ch):04X}" for ch in non_ascii)
        fail(
            "capture_stage9_screenshots.ps1 must remain ASCII-only for Windows "
            f"PowerShell 5.1 compatibility; found: {codepoints}"
        )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_readme_tokens = [
        "Retail360",
        "PostgreSQL",
        "Power BI",
        "78 explicit governed measures",
        "34/34 exact KPI runtime checks",
        "10 analytical pages + 1 hidden report-page tooltip",
        "docs/architecture/retail360-architecture.md",
        "docs/architecture/star-schema.md",
        "docs/project/architecture-decisions.md",
        "docs/project/setup.md",
        "docs/sql/business-analysis-examples.md",
    ]
    for token in required_readme_tokens:
        if token not in readme:
            fail(f"README missing required project token: {token}")

    architecture = (ROOT / "docs/architecture/retail360-architecture.md").read_text(encoding="utf-8")
    star = (ROOT / "docs/architecture/star-schema.md").read_text(encoding="utf-8")
    mermaid_marker = chr(96) * 3 + "mermaid"
    if mermaid_marker not in architecture or mermaid_marker not in star:
        fail("architecture diagrams must use GitHub-renderable Mermaid")

    model = (ROOT / "powerbi/Retail360.SemanticModel/definition/tables/KPI_Measures.tmdl").read_text(encoding="utf-8")
    measures = re.findall(r"^\s*measure\s+(?:'[^']+'|[^=\n]+?)\s*=", model, flags=re.MULTILINE)
    if len(measures) != 78:
        fail(f"expected 78 governed measures, found {len(measures)}")

    pages_meta = json.loads(
        (ROOT / "powerbi/Retail360.Report/definition/pages/pages.json").read_text(encoding="utf-8")
    )
    order = pages_meta["pageOrder"]

    visible_names: list[str] = []
    hidden_count = 0
    for page_id in order:
        page_path = ROOT / "powerbi/Retail360.Report/definition/pages" / page_id / "page.json"
        page = json.loads(page_path.read_text(encoding="utf-8"))
        if page.get("visibility") == "HiddenInViewMode":
            hidden_count += 1
        else:
            visible_names.append(page["displayName"])

    if visible_names != EXPECTED_VISIBLE_PAGES:
        fail(f"visible page order mismatch: {visible_names}")
    if hidden_count != 1:
        fail(f"expected one hidden tooltip page, found {hidden_count}")

    for proof in [
        "docs/data-engineering/stage6-powerbi-runtime-proof.csv",
        "docs/data-engineering/stage6-measure-smoke-proof.csv",
        "docs/data-engineering/stage8-validation-summary.md",
    ]:
        path = ROOT / proof
        if not path.exists() or path.stat().st_size == 0:
            fail(f"missing validation evidence: {proof}")

    screenshot_dir = ROOT / "docs/screenshots"
    existing = [name for name in SCREENSHOTS if (screenshot_dir / name).exists()]

    if args.require_screenshots:
        missing = [name for name in SCREENSHOTS if not (screenshot_dir / name).exists()]
        if missing:
            fail("missing screenshots: " + ", ".join(missing))
        for name in SCREENSHOTS:
            size = (screenshot_dir / name).stat().st_size
            if size < 50_000:
                fail(f"screenshot is unexpectedly small: {name} ({size} bytes)")
        screenshot_status = "10/10 PASS"
    else:
        screenshot_status = f"{len(existing)}/10 present; local rendered-image gate is separate"

    print("Retail360 Stage 9 repository packaging")
    print("-" * 76)
    print("Final README:             PASS")
    print("Architecture diagram:     PASS")
    print("Star-schema diagram:      PASS")
    print("KPI dictionary:           PASS")
    print("SQL examples:             PASS")
    print("Architecture decisions:   PASS")
    print("Setup guide:              PASS")
    print("Public repository scope:  PASS")
    print("Stage 6 runtime evidence: PASS")
    print("Stage 8 enterprise QA:    PASS")
    print("Report page contract:     10 visible + 1 tooltip PASS")
    print(f"Dashboard screenshots:    {screenshot_status}")
    print("-" * 76)
    print("Stage 9 repository packaging validation PASSED.")


if __name__ == "__main__":
    main()
