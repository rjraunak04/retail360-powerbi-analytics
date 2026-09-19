from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASURES = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "tables" / "Measures.tmdl"
MODEL = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "model.tmdl"
QA = ROOT / "powerbi" / "Retail360.SemanticModel" / "DAXQueries" / "Stage6 KPI QA.dax"

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

    text = MEASURES.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    qa = QA.read_text(encoding="utf-8")

    names = set(re.findall(r"^\s*measure\s+(?:'([^']+)'|([^=\n]+?))\s*=", text, re.MULTILINE))
    measure_names = {a or b.strip() for a, b in names}

    missing = REQUIRED_MEASURES - measure_names
    if missing:
        fail(f"missing required measures: {sorted(missing)}")

    if len(measure_names) < 60:
        fail(f"expected at least 60 governed measures, found {len(measure_names)}")

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
    print("Runtime QA contract:    20 checks PASS")
    print("-" * 72)
    print("Stage 6 DAX contract PASSED.")


if __name__ == "__main__":
    main()
