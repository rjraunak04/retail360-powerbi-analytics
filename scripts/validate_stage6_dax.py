from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASURES = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "tables" / "Measures.tmdl"
MODEL = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "model.tmdl"
QA = ROOT / "powerbi" / "Retail360.SemanticModel" / "DAXQueries" / "Stage6 KPI QA.dax"
QA_MIRROR = ROOT / "dax" / "qa" / "stage6_kpi_qa.dax"
RUNTIME = ROOT / "scripts" / "verify_powerbi_stage6_runtime.ps1"

REQUIRED_MEASURES = {
    "Total Sales", "Units Sold", "Distinct Orders", "Average Selling Price",
    "Average Order Value", "Total Product Cost", "Gross Profit", "Gross Margin %",
    "Sales MTD", "Sales QTD", "Sales YTD", "Sales PY", "Sales YoY", "Sales YoY %",
    "Sales MoM %", "Profit YTD", "Profit YoY %", "Sales by Due Date",
    "Sales by Ship Date", "Customers", "Revenue per Customer", "Repeat Customers",
    "Repeat Customer %", "Resellers", "Revenue per Reseller", "Products Sold",
    "Product Rank by Sales", "Category Rank by Sales", "Internet Sales",
    "Reseller Sales", "Internet Sales %", "Reseller Sales %", "Discounted Sales",
    "Discounted Sales %", "Current Inventory Value", "Current Inventory Units",
    "Average Inventory Value", "Inventory Turnover", "Products Below Safety Stock",
    "Products Below Reorder Point", "Inventory Health %", "Selected Period Label",
    "Executive Overview Title", "Inventory Title",
}

REQUIRED_FOLDERS = {
    "Sales & Volume", "Profitability", "Growth & Time Intelligence",
    "Role-Playing Dates", "Customer & Reseller", "Product", "Channel",
    "Promotion", "Inventory", "UX & Dynamic Titles",
}


def fail(message: str) -> None:
    raise SystemExit(f"Stage 6 DAX contract FAILED: {message}")


def main() -> None:
    if not MEASURES.exists():
        fail("Measures.tmdl is missing")
    if not QA.exists():
        fail("Stage6 KPI QA.dax is missing")
    if not QA_MIRROR.exists():
        fail("dax/qa/stage6_kpi_qa.dax mirror is missing")
    if not RUNTIME.exists():
        fail("Stage 6 Power BI runtime verifier is missing")

    text = MEASURES.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    qa = QA.read_text(encoding="utf-8")

    names = set(re.findall(r"^\s*measure\s+(?:'([^']+)'|([^=\n]+?))\s*=", text, re.MULTILINE))
    measure_names = {a or b.strip() for a, b in names}

    missing = REQUIRED_MEASURES - measure_names
    if missing:
        fail(f"missing required measures: {sorted(missing)}")

    if len(measure_names) < 75:
        fail(f"expected at least 75 governed measures, found {len(measure_names)}")

    folders = set(re.findall(r"^\s*displayFolder:\s*(.+?)\s*$", text, re.MULTILINE))
    missing_folders = REQUIRED_FOLDERS - folders
    if missing_folders:
        fail(f"missing display folders: {sorted(missing_folders)}")

    if "AVERAGE(FactSales[Gross Margin Pct])" in text.replace(" ", ""):
        fail("Gross Margin % must never average the row-level margin column")

    required_tokens = [
        "DIVIDE([Gross Profit], [Total Sales])",
        "DATESMTD(DimDate[Date])",
        "DATESQTD(DimDate[Date])",
        "DATESYTD(DimDate[Date])",
        "SAMEPERIODLASTYEAR(DimDate[Date])",
        "USERELATIONSHIP(FactSales[Due Date Key], DimDate[Date Key])",
        "USERELATIONSHIP(FactSales[Ship Date Key], DimDate[Date Key])",
        "REMOVEFILTERS(DimDate)",
        "ALLSELECTED(DimProduct",
        "RANKX(",
    ]
    for token in required_tokens:
        if token not in text:
            fail(f"required DAX pattern missing: {token}")

    if "ref table Measures" not in model:
        fail("model.tmdl does not reference Measures")
    if "partition Measures = calculated" not in text:
        fail("Measures table must use a calculated one-row partition")
    if 'source = ROW("Value", 0)' not in text:
        fail("Measures calculated partition source is not the expected one-row table")

    qa_mirror = QA_MIRROR.read_text(encoding="utf-8")
    if qa != qa_mirror:
        fail("Stage 6 DAX QA mirror differs from the PBIP DAX query")

    if qa.count('ROW("Check"') != 20:
        fail("Stage6 KPI QA must contain exactly 20 checks")
    if "Gross Margin identity" not in qa or "Channel reconciliation" not in qa:
        fail("Stage6 KPI QA is missing reconciliation checks")

    print("Retail360 Stage 6 DAX KPI contract")
    print("-" * 72)
    print(f"Governed measures: {len(measure_names):>3} PASS")
    print(f"Required measures: {len(REQUIRED_MEASURES):>3}/{len(REQUIRED_MEASURES)} PASS")
    print(f"Display folders:   {len(REQUIRED_FOLDERS):>3}/{len(REQUIRED_FOLDERS)} PASS")
    print("Weighted margin:        PASS")
    print("Time intelligence:      PASS")
    print("Role-playing dates:     PASS")
    print("Inventory snapshot DAX: PASS")
    print("Product ranking/share:  PASS")
    if "$" in text or "€" in text or "£" in text or "₹" in text:
        fail("currency symbol found in governed measures despite unresolved currency conversion semantics")

    runtime = RUNTIME.read_text(encoding="utf-8")
    for token in ("Stage6 KPI QA.dax", "stage6-powerbi-runtime-proof.csv", 'StageLabel "Stage 6"'):
        if token not in runtime:
            fail(f"runtime verifier missing token: {token}")

    print("Runtime QA contract:    20 checks PASS")
    print("QA mirror consistency:  PASS")
    print("Neutral currency format: PASS")
    print("Runtime verifier:       PASS")
    print("-" * 72)
    print("Stage 6 DAX contract PASSED.")


if __name__ == "__main__":
    main()
