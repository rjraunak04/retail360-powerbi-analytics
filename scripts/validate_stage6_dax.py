from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASURES = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "tables" / "Measures.tmdl"
MODEL = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "model.tmdl"
QA = ROOT / "powerbi" / "Retail360.SemanticModel" / "DAXQueries" / "Stage6 KPI QA.dax"
QA_COPY = ROOT / "dax" / "qa" / "stage6_kpi_qa.dax"
SMOKE = ROOT / "powerbi" / "Retail360.SemanticModel" / "DAXQueries" / "Stage6 Measure Smoke QA.dax"
SMOKE_COPY = ROOT / "dax" / "qa" / "stage6_measure_smoke_qa.dax"

REQUIRED_MEASURES = {
    "Total Sales", "Units Sold", "Sales Lines", "Distinct Orders",
    "Average Selling Price", "Average Order Value", "Average Units per Order",
    "Total Discount Amount", "Discount Rate", "Total Tax", "Total Freight",
    "Total Product Cost", "Gross Profit", "Gross Margin %", "Profit per Unit",
    "Profit per Order", "Sales MTD", "Sales QTD", "Sales YTD", "Sales PY",
    "Sales YoY", "Sales YoY %", "Sales Previous Month", "Sales MoM",
    "Sales MoM %", "Profit YTD", "Profit PY", "Profit YoY", "Profit YoY %",
    "Units YTD", "Units PY", "Units YoY %", "Sales by Due Date",
    "Sales by Ship Date", "Orders by Due Date", "Orders by Ship Date",
    "Customers", "Revenue per Customer", "Repeat Customers", "Repeat Customer %",
    "Resellers", "Revenue per Reseller", "Reseller Orders", "Products Sold",
    "Product Sales Share %", "Product Rank by Sales", "Category Sales Share %",
    "Category Rank by Sales", "Internet Sales", "Reseller Sales",
    "Internet Sales %", "Reseller Sales %", "Internet Orders", "Discounted Sales",
    "Discounted Sales %", "Discounted Orders", "Average Discount per Discounted Order",
    "Inventory Value (Snapshot Context)", "Inventory Units Balance",
    "Inventory Units In", "Inventory Units Out", "Net Inventory Movement",
    "Latest Inventory Date", "Current Inventory Value", "Current Inventory Units",
    "Average Inventory Value", "Inventory Turnover", "Products With Inventory",
    "Products Below Safety Stock", "Products Below Reorder Point",
    "Inventory Health %", "Selected Period Label", "Executive Overview Title",
    "Sales Growth Title", "Product Profitability Title", "Inventory Title",
}

REQUIRED_FOLDERS = {
    "Sales & Volume",
    "Profitability",
    "Growth & Time Intelligence",
    "Role-Playing Dates",
    "Customer & Reseller",
    "Product",
    "Channel",
    "Promotion",
    "Inventory",
    "UX & Dynamic Titles",
}

REQUIRED_DAX_PATTERNS = {
    "weighted gross margin": "DIVIDE([Gross Profit], [Total Sales])",
    "month-to-date": "DATESMTD(DimDate[Date])",
    "quarter-to-date": "DATESQTD(DimDate[Date])",
    "year-to-date": "DATESYTD(DimDate[Date])",
    "prior year": "SAMEPERIODLASTYEAR(DimDate[Date])",
    "due-date role": "USERELATIONSHIP(FactSales[Due Date Key], DimDate[Date Key])",
    "ship-date role": "USERELATIONSHIP(FactSales[Ship Date Key], DimDate[Date Key])",
    "latest snapshot": "REMOVEFILTERS(DimDate)",
    "selection-aware product contribution": "ALLSELECTED(DimProduct",
    "ranking": "RANKX(",
}


def fail(message: str) -> None:
    raise SystemExit(f"Stage 6 DAX contract FAILED: {message}")


def main() -> None:
    for required in (MEASURES, MODEL, QA, QA_COPY, SMOKE, SMOKE_COPY):
        if not required.exists():
            fail(f"missing {required.relative_to(ROOT)}")

    text = MEASURES.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    qa = QA.read_text(encoding="utf-8")
    qa_copy = QA_COPY.read_text(encoding="utf-8")
    smoke = SMOKE.read_text(encoding="utf-8")
    smoke_copy = SMOKE_COPY.read_text(encoding="utf-8")

    if qa != qa_copy:
        fail("the source QA query and PBIP DAXQueries copy have drifted")
    if smoke != smoke_copy:
        fail("the source measure-smoke query and PBIP DAXQueries copy have drifted")

    names = set(
        re.findall(
            r"^\s*measure\s+(?:'([^']+)'|([^=\n]+?))\s*=",
            text,
            re.MULTILINE,
        )
    )
    measure_names = {a or b.strip() for a, b in names}

    missing = REQUIRED_MEASURES - measure_names
    unexpected_missing_count = len(measure_names) < len(REQUIRED_MEASURES)
    if missing:
        fail(f"missing governed measures: {sorted(missing)}")
    if unexpected_missing_count:
        fail(
            f"expected at least {len(REQUIRED_MEASURES)} governed measures, "
            f"found {len(measure_names)}"
        )

    folder_assignments = re.findall(
        r"^\s*displayFolder:\s*(.+?)\s*$",
        text,
        re.MULTILINE,
    )
    folders = set(folder_assignments)
    missing_folders = REQUIRED_FOLDERS - folders
    if missing_folders:
        fail(f"missing display folders: {sorted(missing_folders)}")
    if len(folder_assignments) != len(measure_names):
        fail(
            "every governed measure must have exactly one display-folder assignment "
            f"({len(folder_assignments)} folders for {len(measure_names)} measures)"
        )

    compact = re.sub(r"\s+", "", text)
    if "AVERAGE(FactSales[GrossMarginPct])" in compact:
        fail("Gross Margin % must never average the row-level margin column")

    for label, token in REQUIRED_DAX_PATTERNS.items():
        if token not in text:
            fail(f"required {label} DAX pattern missing: {token}")

    if "ref table Measures" not in model:
        fail("model.tmdl does not reference Measures")
    if "partition Measures = calculated" not in text:
        fail("Measures table must use a calculated one-row partition")
    if 'source = ROW("Value", 0)' not in text:
        fail("Measures calculated partition source is not the expected one-row table")

    if "$" in text or "USD" in text:
        fail("consolidated measures must not claim a currency without rate semantics")

    check_count = qa.count('ROW("Check"')
    if check_count != 26:
        fail(f"Stage 6 runtime QA must contain exactly 26 checks, found {check_count}")

    smoke_count = smoke.count('ROW("Check"')
    if smoke_count != len(REQUIRED_MEASURES):
        fail(
            f"Stage 6 measure smoke QA must contain {len(REQUIRED_MEASURES)} checks, "
            f"found {smoke_count}"
        )
    missing_smoke = {
        name for name in REQUIRED_MEASURES
        if f'ROW("Check", "{name}"' not in smoke
    }
    if missing_smoke:
        fail(f"measure smoke QA is missing governed measures: {sorted(missing_smoke)}")

    required_qa_checks = {
        "Gross Margin identity",
        "Channel reconciliation",
        "Internet Sales",
        "Reseller Sales",
        "Customers",
        "Repeat Customers",
        "Latest Inventory Date",
        "Current Inventory Value",
        "Products Below Safety Stock",
        "Products Below Reorder Point",
        "Sales PY under 2014 context",
        "Sales YTD under 2013 context",
        "Profit PY under 2014 context",
    }
    missing_qa = {name for name in required_qa_checks if f'"{name}"' not in qa}
    if missing_qa:
        fail(f"runtime QA is missing checks: {sorted(missing_qa)}")

    print("Retail360 Stage 6 DAX KPI contract")
    print("-" * 76)
    print(f"Governed measures:       {len(measure_names):>3}/{len(REQUIRED_MEASURES)} PASS")
    print(f"Display folders:         {len(REQUIRED_FOLDERS):>3}/{len(REQUIRED_FOLDERS)} PASS")
    print("Explicit measure folders:    PASS")
    print("Weighted margin policy:       PASS")
    print("Time intelligence:            PASS")
    print("Role-playing dates:           PASS")
    print("Latest-snapshot inventory:    PASS")
    print("Product ranking/contribution: PASS")
    print("Neutral currency formatting:  PASS")
    print("QA copies synchronized:       PASS")
    print("Exact runtime QA:             26/26 checks defined")
    print(f"All-measure smoke QA:         {smoke_count}/{len(REQUIRED_MEASURES)} checks defined")
    print("-" * 76)
    print("Stage 6 DAX contract PASSED.")


if __name__ == "__main__":
    main()
