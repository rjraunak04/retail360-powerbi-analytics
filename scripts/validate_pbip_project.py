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
MEASURE_HOST_TABLE = "KPI_Measures"\nEXPECTED_TABLES = SOURCE_TABLES | {MEASURE_HOST_TABLE}\nRESERVED_TABLE_NAMES = {"Measures"}


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
    table_files = {p.stem for p in (DEFINITION / "tables").glob("*.tmdl")}
    if table_files != EXPECTED_TABLES:
        fail(f"table-file set mismatch: {sorted(table_files)}")

    for table in EXPECTED_TABLES:
        if f"ref table {table}" not in model_text:
            fail(f"model.tmdl missing ref table {table}")

        t = (DEFINITION / "tables" / f"{table}.tmdl").read_text(encoding="utf-8")
        if f"table {table}" not in t:
            fail(f"{table}.tmdl missing table declaration")
        if table in SOURCE_TABLES:
            if "PostgreSQL.Database(pServer, pDatabase" not in t:
                fail(f"{table}.tmdl is not parameterized to PostgreSQL")
            if "\t\tmode: import" not in t:
                fail(f"{table}.tmdl is not Import mode")
        else:
            if "partition Measures = calculated" not in t:
                fail("Measures table is not a calculated measure-host table")

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
    print("PBIP shortcut:        PASS")
    print("Report -> Model path: PASS")
    print("Semantic tables:      13/13 PASS")
    print("Relationships:        14/14 PASS")
    print("Inactive date roles:   2/2 PASS")
    print("PostgreSQL parameters: PASS")
    print("Source partitions:    12/12 PASS")
    print("Starter report page:  PASS")
    print("-" * 72)
    print("PBIP scaffold validation PASSED.")


if __name__ == "__main__":
    main()
