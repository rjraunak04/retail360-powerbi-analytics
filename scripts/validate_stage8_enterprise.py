from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition"
ROLES = MODEL / "roles"
TABLES = MODEL / "tables"
RELATIONSHIPS = MODEL / "relationships.tmdl"
MODEL_FILE = MODEL / "model.tmdl"
REPORT_PAGES = ROOT / "powerbi" / "Retail360.Report" / "definition" / "pages"

EXPECTED_ROLES = {
    "RLS_North_America": "North America",
    "RLS_Europe": "Europe",
    "RLS_Pacific": "Pacific",
}

EXPECTED_RELATIONSHIPS = {
    ("FactSales", "Channel Key", "DimChannel", "Channel Key", True),
    ("FactSales", "Product Key", "DimProduct", "Product Key", True),
    ("FactSales", "Order Date Key", "DimDate", "Date Key", True),
    ("FactSales", "Due Date Key", "DimDate", "Date Key", False),
    ("FactSales", "Ship Date Key", "DimDate", "Date Key", False),
    ("FactSales", "Customer Key", "DimCustomer", "Customer Key", True),
    ("FactSales", "Reseller Key", "DimReseller", "Reseller Key", True),
    ("FactSales", "Employee Key", "DimEmployee", "Employee Key", True),
    ("FactSales", "Promotion Key", "DimPromotion", "Promotion Key", True),
    ("FactSales", "Currency Key", "DimCurrency", "Currency Key", True),
    ("FactSales", "Sales Territory Key", "DimSalesTerritory", "Sales Territory Key", True),
    ("FactSales", "Geography Key", "DimGeography", "Geography Key", True),
    ("FactInventory", "Product Key", "DimProduct", "Product Key", True),
    ("FactInventory", "Date Key", "DimDate", "Date Key", True),
}

ALLOWED_VISUALS = {"textbox", "cardVisual", "slicer", "lineChart", "barChart", "tableEx"}


def fail(message: str) -> None:
    raise SystemExit(f"Stage 8 enterprise contract FAILED: {message}")


def parse_endpoint(raw: str) -> tuple[str, str]:
    m = re.fullmatch(r"([A-Za-z0-9_]+)\.'([^']+)'", raw.strip())
    if not m:
        fail(f"cannot parse relationship endpoint: {raw}")
    return m.group(1), m.group(2)


def validate_roles(model_text: str) -> None:
    if not ROLES.exists():
        fail("semantic-model roles folder is missing")

    actual_files = {p.stem for p in ROLES.glob("*.tmdl")}
    if actual_files != set(EXPECTED_ROLES):
        fail(f"RLS role-file set mismatch: {sorted(actual_files)}")

    for role, group in EXPECTED_ROLES.items():
        text = (ROLES / f"{role}.tmdl").read_text(encoding="utf-8")
        if f"role {role}" not in text:
            fail(f"{role} declaration is missing")
        if "modelPermission: read" not in text:
            fail(f"{role} must use read model permission")
        expected_filter = (
            'tablePermission DimSalesTerritory = '
            f'DimSalesTerritory[Territory Group] = "{group}"'
        )
        if expected_filter not in text:
            fail(f"{role} territory filter is incorrect")
        if "tablePermission FactInventory = FALSE()" not in text:
            fail(f"{role} must deny unscoped inventory rows")
        if re.search(r"^\s*member\s+", text, re.M):
            fail(f"{role} hard-codes identity membership in source control")
        if f"ref role {role}" not in model_text:
            fail(f"model.tmdl does not register {role}")


def validate_relationships() -> None:
    text = RELATIONSHIPS.read_text(encoding="utf-8")
    if "crossfilteringbehavior: both" in text.lower():
        fail("bidirectional relationship found")
    if "securityfilteringbehavior: both" in text.lower():
        fail("bidirectional security filtering found")

    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    found = set()
    for block in blocks:
        if not block.startswith("relationship "):
            continue
        fm = re.search(r"fromColumn:\s*(.+)", block)
        tm = re.search(r"toColumn:\s*(.+)", block)
        if not fm or not tm:
            fail("relationship missing fromColumn/toColumn")
        ft, fc = parse_endpoint(fm.group(1))
        tt, tc = parse_endpoint(tm.group(1))
        active = "isActive: false" not in block
        found.add((ft, fc, tt, tc, active))

        if ft not in {"FactSales", "FactInventory"}:
            fail(f"relationship many-side is not a fact table: {ft}")
        if tt in {"FactSales", "FactInventory", "KPI_Measures"}:
            fail(f"relationship target is not a dimension: {tt}")

    if found != EXPECTED_RELATIONSHIPS:
        missing = EXPECTED_RELATIONSHIPS - found
        extra = found - EXPECTED_RELATIONSHIPS
        fail(f"relationship contract mismatch; missing={sorted(missing)}, extra={sorted(extra)}")


def validate_dax() -> None:
    text = (TABLES / "KPI_Measures.tmdl").read_text(encoding="utf-8")
    measure_count = len(re.findall(r"^\s*measure\s+", text, re.M))
    if measure_count != 78:
        fail(f"expected 78 governed measures, found {measure_count}")

    required = {
        "weighted gross margin": "measure 'Gross Margin %' = DIVIDE([Gross Profit], [Total Sales])",
        "due-date role": "USERELATIONSHIP(FactSales[Due Date Key], DimDate[Date Key])",
        "ship-date role": "USERELATIONSHIP(FactSales[Ship Date Key], DimDate[Date Key])",
        "latest inventory variable": "VAR LatestDate = [Latest Inventory Date]",
        "product ranking": "RANKX(",
        "selection-aware contribution": "ALLSELECTED(DimProduct",
    }
    for label, token in required.items():
        if token not in text:
            fail(f"DAX optimization contract missing {label}")

    forbidden = {
        "average row gross margin": "AVERAGE(FactSales[Gross Margin Pct])",
        "fact-table FILTER iterator": "FILTER(FactSales",
        "implicit currency symbol USD": "$#,",
        "implicit currency symbol INR": "₹",
    }
    for label, token in forbidden.items():
        if token in text:
            fail(f"forbidden DAX/performance pattern: {label}")

    ratio_measures = [
        "Gross Margin %",
        "Sales YoY %",
        "Sales MoM %",
        "Profit YoY %",
        "Units YoY %",
        "Internet Sales %",
        "Reseller Sales %",
        "Discounted Sales %",
        "Safety Stock Risk %",
        "Reorder Risk %",
    ]
    for name in ratio_measures:
        m = re.search(
            rf"measure '{re.escape(name)}'\s*=([\s\S]*?)(?=\n\s*(?:measure|column)\s)",
            text,
        )
        if not m or "DIVIDE(" not in m.group(1):
            fail(f"ratio measure {name} must use DIVIDE")

    model_text = MODEL_FILE.read_text(encoding="utf-8")
    if "discourageImplicitMeasures" not in model_text:
        fail("implicit measures are not discouraged")


def validate_report_performance_structure() -> None:
    metadata = json.loads((REPORT_PAGES / "pages.json").read_text(encoding="utf-8"))
    order = metadata.get("pageOrder", [])
    if len(order) != 11:
        fail(f"expected 11 report pages, found {len(order)}")

    total_visuals = 0
    max_visible = 0
    visual_types: set[str] = set()

    for page_id in order:
        page_dir = REPORT_PAGES / page_id
        page = json.loads((page_dir / "page.json").read_text(encoding="utf-8"))
        visuals = []
        vdir = page_dir / "visuals"
        if vdir.exists():
            for path in vdir.glob("*/visual.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                visuals.append(data)
                vtype = ((data.get("visual") or {}).get("visualType"))
                if vtype:
                    visual_types.add(vtype)
                    if vtype not in ALLOWED_VISUALS:
                        fail(f"non-native/unapproved visual type found: {vtype}")

        total_visuals += len(visuals)
        if page.get("displayName") == "Product Tooltip":
            if len(visuals) > 2:
                fail("tooltip page exceeds two-visual performance budget")
        else:
            max_visible = max(max_visible, len(visuals))
            if len(visuals) > 6:
                fail(f"{page.get('displayName')} exceeds six-visual performance budget")

    if total_visuals != 62:
        fail(f"expected Stage 7 baseline of 62 visuals, found {total_visuals}")
    if max_visible != 6:
        fail(f"visible-page visual budget drifted; max={max_visible}")


def validate_docs() -> None:
    required = {
        ROOT / "docs/security/rls-design.md": [
            "RLS_North_America", "RLS_Europe", "RLS_Pacific", "FactInventory = FALSE()"
        ],
        ROOT / "docs/qa/performance-analyzer-review.md": [
            "Performance Analyzer", "Distinct Orders", "RANKX", "six native visuals"
        ],
        ROOT / "docs/deployment/powerbi-refresh-deployment.md": [
            "pServer", "pDatabase", "gateway", "Import mode"
        ],
        ROOT / "docs/deployment/pbip-pbix-strategy.md": [
            "canonical", "PBIP", "PBIX", ".pbi"
        ],
        ROOT / "docs/qa/stage8-enterprise-qa.md": [
            "relationship-model QA", "edge-case", "Stage 8"
        ],
    }
    for path, tokens in required.items():
        if not path.exists():
            fail(f"required Stage 8 documentation missing: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                fail(f"{path.relative_to(ROOT)} missing required token: {token}")


def main() -> None:
    model_text = MODEL_FILE.read_text(encoding="utf-8")
    validate_roles(model_text)
    validate_relationships()
    validate_dax()
    validate_report_performance_structure()
    validate_docs()

    print("Retail360 Stage 8 enterprise contract")
    print("-" * 78)
    print("RLS roles:                   3/3 PASS")
    print("Inventory RLS fail-closed:      PASS")
    print("Hard-coded role members:       0 PASS")
    print("Relationships:              14/14 PASS")
    print("Bidirectional relationships:   0 PASS")
    print("Inactive role dates:           2 PASS")
    print("Governed DAX measures:      78/78 PASS")
    print("DAX optimization policy:       PASS")
    print("Report visual budget:       62/62 PASS")
    print("Native visual policy:          PASS")
    print("Refresh/deployment docs:       PASS")
    print("PBIP/PBIX strategy:            PASS")
    print("-" * 78)
    print("Stage 8 enterprise contract PASSED.")


if __name__ == "__main__":
    main()
