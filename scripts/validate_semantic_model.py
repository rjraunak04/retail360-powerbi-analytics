from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "powerbi" / "semantic-model-contract.json"
TMDL = ROOT / "powerbi" / "tmdl" / "stage5_semantic_model.tmdl"
M_DIR = ROOT / "power-query"

EXPECTED_TABLES = {
    "DimDate", "DimProduct", "DimCustomer", "DimReseller", "DimEmployee",
    "DimGeography", "DimSalesTerritory", "DimPromotion", "DimCurrency",
    "DimChannel", "FactSales", "FactInventory",
}


def fail(message: str) -> None:
    raise SystemExit(f"Stage 5 semantic contract FAILED: {message}")


def main() -> None:
    model = json.loads(CONTRACT.read_text(encoding="utf-8"))
    tables = model["tables"]

    if set(tables) != EXPECTED_TABLES:
        fail(f"table set mismatch: {sorted(tables)}")

    if model["storageMode"] != "Import":
        fail("Stage 5 must use Import mode")

    if model["dateTable"] != {"table": "DimDate", "dateColumn": "Date"}:
        fail("date-table contract is not DimDate[Date]")

    for table_name, spec in tables.items():
        columns = {col[0] for col in spec["columns"]}
        source_columns = [col[1] for col in spec["columns"]]

        if len(columns) != len(spec["columns"]):
            fail(f"duplicate semantic column in {table_name}")
        if len(source_columns) != len(set(source_columns)):
            fail(f"duplicate source column mapping in {table_name}")

        key = spec.get("key")
        if key and key not in columns:
            fail(f"{table_name} key does not exist: {key}")

        missing_hidden = set(spec.get("hiddenColumns", [])) - columns
        if missing_hidden:
            fail(f"{table_name} hidden columns missing: {sorted(missing_hidden)}")

        m_file = M_DIR / f"{table_name}.m"
        if not m_file.exists():
            fail(f"missing Power Query file: {m_file.relative_to(ROOT)}")

        m_text = m_file.read_text(encoding="utf-8")
        if f'Item="{spec["source"]}"' not in m_text:
            fail(f"{table_name} Power Query does not target analytics.{spec['source']}")
        if "PostgreSQL.Database(pServer, pDatabase" not in m_text:
            fail(f"{table_name} Power Query does not use governed parameters")

    rel_names = set()
    active_date_relationships = []

    for rel in model["relationships"]:
        name = rel["name"]
        if name in rel_names:
            fail(f"duplicate relationship name: {name}")
        rel_names.add(name)

        from_table, from_column = rel["from"]
        to_table, to_column = rel["to"]

        if from_table not in tables or to_table not in tables:
            fail(f"{name} references missing table")

        from_columns = {col[0] for col in tables[from_table]["columns"]}
        to_columns = {col[0] for col in tables[to_table]["columns"]}

        if from_column not in from_columns:
            fail(f"{name} missing from-column {from_table}[{from_column}]")
        if to_column not in to_columns:
            fail(f"{name} missing to-column {to_table}[{to_column}]")

        if not from_table.startswith("Fact"):
            fail(f"{name} must filter from dimension to fact; from-side must be fact in contract")
        if not to_table.startswith("Dim"):
            fail(f"{name} target must be a dimension")

        if from_table == "FactSales" and to_table == "DimDate" and rel["active"]:
            active_date_relationships.append(name)

    if active_date_relationships != ["Sales_OrderDate"]:
        fail(f"FactSales must have only active Order Date relationship, got {active_date_relationships}")

    required_inactive = {"Sales_DueDate", "Sales_ShipDate"}
    actual_inactive = {r["name"] for r in model["relationships"] if not r["active"]}
    if actual_inactive != required_inactive:
        fail(f"inactive relationship set mismatch: {actual_inactive}")

    if len(model["relationships"]) != 14:
        fail(f"expected 14 relationships, found {len(model['relationships'])}")

    for parameter_file in ("pServer.m", "pDatabase.m"):
        if not (M_DIR / parameter_file).exists():
            fail(f"missing Power Query parameter file: {parameter_file}")

    tmdl = TMDL.read_text(encoding="utf-8")
    for table_name in EXPECTED_TABLES:
        if f"        table {table_name}\n" not in tmdl:
            fail(f"TMDL missing or mis-indented table {table_name}")
        if f"            partition {table_name} = m\n" not in tmdl:
            fail(f"TMDL missing or mis-indented partition {table_name}")

    if "expression pServer" not in tmdl or "expression pDatabase" not in tmdl:
        fail("TMDL missing PostgreSQL parameters")

    if "        table DimDate\n            dataCategory: Time" not in tmdl:
        fail("TMDL does not mark DimDate as a Time table")

    if "            column 'Date'\n" not in tmdl or "                isKey\n" not in tmdl:
        fail("TMDL date-table key metadata missing")

    if tmdl.count("relationship ") != 14:
        fail("TMDL does not contain exactly 14 relationships")

    print("Retail360 Stage 5 semantic-model contract")
    print("-" * 72)
    print(f"Tables:        {len(tables):>3} PASS")
    print(f"Relationships: {len(model['relationships']):>3} PASS")
    print("Storage mode: Import PASS")
    print("Date table:   DimDate[Date] PASS")
    print("Role dates:   Order=active, Due/Ship=inactive PASS")
    print("Power Query:  12/12 analytics sources + 2 parameters PASS")
    print("TMDL script:  structural contract PASS")
    print("-" * 72)
    print("Stage 5 semantic contract PASSED.")


if __name__ == "__main__":
    main()
