from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
PBIP = PBI / "Retail360.pbip"
REPORT = PBI / "Retail360.Report"
MODEL = PBI / "Retail360.SemanticModel"
DEFINITION = MODEL / "definition"

SOURCE_TABLES = {
    "DimDate", "DimProduct", "DimCustomer", "DimReseller", "DimEmployee",
    "DimGeography", "DimSalesTerritory", "DimPromotion", "DimCurrency",
    "DimChannel", "FactSales", "FactInventory",
}
MEASURE_HOST_TABLE = "KPI_Measures"
EXPECTED_TABLES = SOURCE_TABLES | {MEASURE_HOST_TABLE}
RESERVED_TABLE_NAMES = {"Measures"}


def fail(message: str) -> None:
    raise SystemExit(f"PBIP validation FAILED: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    required = [
        PBIP,
        MODEL / "definition.pbism",
        DEFINITION / "database.tmdl",
        DEFINITION / "model.tmdl",
        DEFINITION / "expressions.tmdl",
        DEFINITION / "relationships.tmdl",
        REPORT / "definition.pbir",
        REPORT / "definition" / "report.json",
        REPORT / "definition" / "version.json",
        REPORT / "definition" / "pages" / "pages.json",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")

    pbip = load_json(PBIP)
    report_ref = pbip["artifacts"][0]["report"]["path"]
    if report_ref != "Retail360.Report":
        fail(f"Retail360.pbip report path mismatch: {report_ref}")

    pbir = load_json(REPORT / "definition.pbir")
    model_ref = pbir["datasetReference"]["byPath"]["path"]
    if model_ref != "../Retail360.SemanticModel":
        fail(f"definition.pbir semantic-model path mismatch: {model_ref}")

    pbism = load_json(MODEL / "definition.pbism")
    if float(pbism["version"]) < 4.0:
        fail("definition.pbism must be version 4.0+")

    model_text = (DEFINITION / "model.tmdl").read_text(encoding="utf-8")
    table_dir = DEFINITION / "tables"
    table_files = {p.stem for p in table_dir.glob("*.tmdl")}

    reserved = table_files & RESERVED_TABLE_NAMES
    if reserved:
        fail(f"reserved/unsupported Power BI table name(s): {sorted(reserved)}")

    if table_files != EXPECTED_TABLES:
        fail(f"table-file set mismatch: {sorted(table_files)}")

    for table in EXPECTED_TABLES:
        if f"ref table {table}" not in model_text:
            fail(f"model.tmdl missing ref table {table}")

        t = (table_dir / f"{table}.tmdl").read_text(encoding="utf-8")
        if f"table {table}" not in t:
            fail(f"{table}.tmdl missing table declaration")

        if table in SOURCE_TABLES:
            compact_t = "".join(t.split())
            if "PostgreSQL.Database(pServer,pDatabase" not in compact_t:
                fail(f"{table}.tmdl is not parameterized to PostgreSQL")
            if "\t\tmode: import" not in t:
                fail(f"{table}.tmdl is not Import mode")
        else:
            if f"partition {MEASURE_HOST_TABLE} = m" not in t:
                fail(f"{MEASURE_HOST_TABLE} must use a static M partition")
            if '#table(type table [Value = Int64.Type], {{0}})' not in t:
                fail(f"{MEASURE_HOST_TABLE} static M partition source is invalid")

    if '"Measures"' in model_text or "ref table Measures" in model_text:
        fail('model.tmdl still contains the reserved table name "Measures"')

    query_order_line = next(
        (line for line in model_text.splitlines() if line.startswith("annotation PBI_QueryOrder")),
        "",
    )
    if MEASURE_HOST_TABLE not in query_order_line:
        fail("static KPI_Measures table must appear in Power Query order")

    fact_inventory_text = (table_dir / "FactInventory.tmdl").read_text(encoding="utf-8")
    if 'Query="SELECT product_key, date_key, movement_date, unit_cost, units_in, units_out, units_balance, net_units_movement, inventory_value FROM analytics.fact_inventory"' not in fact_inventory_text:
        fail("FactInventory must use the direct SQL import path to avoid navigator evaluation cycles")
    if 'Item="fact_inventory"' in fact_inventory_text:
        fail("FactInventory still uses navigator lookup and may reintroduce cyclic evaluation")

    expr = (DEFINITION / "expressions.tmdl").read_text(encoding="utf-8")
    if "expression pServer" not in expr or "expression pDatabase" not in expr:
        fail("Power Query parameters are missing")

    rel = (DEFINITION / "relationships.tmdl").read_text(encoding="utf-8")
    if rel.count("relationship ") != 14:
        fail(f"expected 14 relationships, found {rel.count('relationship ')}")
    if rel.count("isActive: false") != 2:
        fail("expected exactly two inactive role-playing date relationships")

    pages = load_json(REPORT / "definition" / "pages" / "pages.json")
    if len(pages.get("pageOrder", [])) != 1:
        fail("starter report must contain exactly one page")

    page_id = pages["pageOrder"][0]
    page = REPORT / "definition" / "pages" / page_id / "page.json"
    if not page.exists():
        fail(f"page definition missing for {page_id}")

    print("Retail360 PBIP scaffold")
    print("-" * 72)
    print("PBIP shortcut:          PASS")
    print("Report -> Model path:   PASS")
    print("Semantic tables:        13/13 PASS")
    print("Reserved table names:   PASS")
    print("KPI measure host:       KPI_Measures static-M PASS")
    print("FactInventory import:   direct SQL PASS")
    print("Relationships:          14/14 PASS")
    print("Inactive date roles:     2/2 PASS")
    print("PostgreSQL parameters:  PASS")
    print("Source partitions:      12/12 PASS")
    print("Starter report page:    PASS")
    print("-" * 72)
    print("PBIP scaffold validation PASSED.")


if __name__ == "__main__":
    main()
