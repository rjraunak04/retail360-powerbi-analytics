from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

RAW_DIR = Path("data/raw/adventureworks")
REPORT_DIR = Path("docs/data-model")

SCHEMAS: dict[str, list[str]] = {
    "DimCurrency": [
        "CurrencyKey", "CurrencyAlternateKey", "CurrencyName",
    ],
    "DimCustomer": [
        "CustomerKey", "GeographyKey", "CustomerAlternateKey", "Title",
        "FirstName", "MiddleName", "LastName", "NameStyle", "BirthDate",
        "MaritalStatus", "Suffix", "Gender", "EmailAddress", "YearlyIncome",
        "TotalChildren", "NumberChildrenAtHome", "EnglishEducation",
        "SpanishEducation", "FrenchEducation", "EnglishOccupation",
        "SpanishOccupation", "FrenchOccupation", "HouseOwnerFlag",
        "NumberCarsOwned", "AddressLine1", "AddressLine2", "Phone",
        "DateFirstPurchase", "CommuteDistance",
    ],
    "DimDate": [
        "DateKey", "FullDateAlternateKey", "DayNumberOfWeek",
        "EnglishDayNameOfWeek", "SpanishDayNameOfWeek", "FrenchDayNameOfWeek",
        "DayNumberOfMonth", "DayNumberOfYear", "WeekNumberOfYear",
        "EnglishMonthName", "SpanishMonthName", "FrenchMonthName",
        "MonthNumberOfYear", "CalendarQuarter", "CalendarYear",
        "CalendarSemester", "FiscalQuarter", "FiscalYear", "FiscalSemester",
    ],
    "DimEmployee": [
        "EmployeeKey", "ParentEmployeeKey", "EmployeeNationalIDAlternateKey",
        "ParentEmployeeNationalIDAlternateKey", "SalesTerritoryKey",
        "FirstName", "LastName", "MiddleName", "NameStyle", "Title",
        "HireDate", "BirthDate", "LoginID", "EmailAddress", "Phone",
        "MaritalStatus", "EmergencyContactName", "EmergencyContactPhone",
        "SalariedFlag", "Gender", "PayFrequency", "BaseRate",
        "VacationHours", "SickLeaveHours", "CurrentFlag", "SalesPersonFlag",
        "DepartmentName", "StartDate", "EndDate", "Status", "EmployeePhoto",
    ],
    "DimGeography": [
        "GeographyKey", "City", "StateProvinceCode", "StateProvinceName",
        "CountryRegionCode", "EnglishCountryRegionName",
        "SpanishCountryRegionName", "FrenchCountryRegionName", "PostalCode",
        "SalesTerritoryKey", "IpAddressLocator",
    ],
    "DimProduct": [
        "ProductKey", "ProductAlternateKey", "ProductSubcategoryKey",
        "WeightUnitMeasureCode", "SizeUnitMeasureCode", "EnglishProductName",
        "SpanishProductName", "FrenchProductName", "StandardCost",
        "FinishedGoodsFlag", "Color", "SafetyStockLevel", "ReorderPoint",
        "ListPrice", "Size", "SizeRange", "Weight", "DaysToManufacture",
        "ProductLine", "DealerPrice", "Class", "Style", "ModelName",
        "LargePhoto", "EnglishDescription", "FrenchDescription",
        "ChineseDescription", "ArabicDescription", "HebrewDescription",
        "ThaiDescription", "GermanDescription", "JapaneseDescription",
        "TurkishDescription", "StartDate", "EndDate", "Status",
    ],
    "DimProductCategory": [
        "ProductCategoryKey", "ProductCategoryAlternateKey",
        "EnglishProductCategoryName", "SpanishProductCategoryName",
        "FrenchProductCategoryName",
    ],
    "DimProductSubcategory": [
        "ProductSubcategoryKey", "ProductSubcategoryAlternateKey",
        "EnglishProductSubcategoryName", "SpanishProductSubcategoryName",
        "FrenchProductSubcategoryName", "ProductCategoryKey",
    ],
    "DimPromotion": [
        "PromotionKey", "PromotionAlternateKey", "EnglishPromotionName",
        "SpanishPromotionName", "FrenchPromotionName", "DiscountPct",
        "EnglishPromotionType", "SpanishPromotionType", "FrenchPromotionType",
        "EnglishPromotionCategory", "SpanishPromotionCategory",
        "FrenchPromotionCategory", "StartDate", "EndDate", "MinQty", "MaxQty",
    ],
    "DimReseller": [
        "ResellerKey", "GeographyKey", "ResellerAlternateKey", "Phone",
        "BusinessType", "ResellerName", "NumberEmployees", "OrderFrequency",
        "OrderMonth", "FirstOrderYear", "LastOrderYear", "ProductLine",
        "AddressLine1", "AddressLine2", "AnnualSales", "BankName",
        "MinPaymentType", "MinPaymentAmount", "AnnualRevenue", "YearOpened",
    ],
    "DimSalesTerritory": [
        "SalesTerritoryKey", "SalesTerritoryAlternateKey",
        "SalesTerritoryRegion", "SalesTerritoryCountry",
        "SalesTerritoryGroup", "SalesTerritoryImage",
    ],
    "FactInternetSales": [
        "ProductKey", "OrderDateKey", "DueDateKey", "ShipDateKey",
        "CustomerKey", "PromotionKey", "CurrencyKey", "SalesTerritoryKey",
        "SalesOrderNumber", "SalesOrderLineNumber", "RevisionNumber",
        "OrderQuantity", "UnitPrice", "ExtendedAmount",
        "UnitPriceDiscountPct", "DiscountAmount", "ProductStandardCost",
        "TotalProductCost", "SalesAmount", "TaxAmt", "Freight",
        "CarrierTrackingNumber", "CustomerPONumber", "OrderDate", "DueDate",
        "ShipDate",
    ],
    "FactResellerSales": [
        "ProductKey", "OrderDateKey", "DueDateKey", "ShipDateKey",
        "ResellerKey", "EmployeeKey", "PromotionKey", "CurrencyKey",
        "SalesTerritoryKey", "SalesOrderNumber", "SalesOrderLineNumber",
        "RevisionNumber", "OrderQuantity", "UnitPrice", "ExtendedAmount",
        "UnitPriceDiscountPct", "DiscountAmount", "ProductStandardCost",
        "TotalProductCost", "SalesAmount", "TaxAmt", "Freight",
        "CarrierTrackingNumber", "CustomerPONumber", "OrderDate", "DueDate",
        "ShipDate",
    ],
    "FactProductInventory": [
        "ProductKey", "DateKey", "MovementDate", "UnitCost",
        "UnitsIn", "UnitsOut", "UnitsBalance",
    ],
}

PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "DimCurrency": ("CurrencyKey",),
    "DimCustomer": ("CustomerKey",),
    "DimDate": ("DateKey",),
    "DimEmployee": ("EmployeeKey",),
    "DimGeography": ("GeographyKey",),
    "DimProduct": ("ProductKey",),
    "DimProductCategory": ("ProductCategoryKey",),
    "DimProductSubcategory": ("ProductSubcategoryKey",),
    "DimPromotion": ("PromotionKey",),
    "DimReseller": ("ResellerKey",),
    "DimSalesTerritory": ("SalesTerritoryKey",),
    "FactInternetSales": ("SalesOrderNumber", "SalesOrderLineNumber"),
    "FactResellerSales": ("SalesOrderNumber", "SalesOrderLineNumber"),
    "FactProductInventory": ("ProductKey", "DateKey"),
}

FOREIGN_KEYS: list[tuple[str, str, str, str, bool]] = [
    ("DimCustomer", "GeographyKey", "DimGeography", "GeographyKey", True),
    ("DimEmployee", "SalesTerritoryKey", "DimSalesTerritory", "SalesTerritoryKey", True),
    ("DimGeography", "SalesTerritoryKey", "DimSalesTerritory", "SalesTerritoryKey", True),
    ("DimProduct", "ProductSubcategoryKey", "DimProductSubcategory", "ProductSubcategoryKey", True),
    ("DimProductSubcategory", "ProductCategoryKey", "DimProductCategory", "ProductCategoryKey", True),
    ("DimReseller", "GeographyKey", "DimGeography", "GeographyKey", True),

    ("FactInternetSales", "ProductKey", "DimProduct", "ProductKey", False),
    ("FactInternetSales", "OrderDateKey", "DimDate", "DateKey", False),
    ("FactInternetSales", "DueDateKey", "DimDate", "DateKey", False),
    ("FactInternetSales", "ShipDateKey", "DimDate", "DateKey", False),
    ("FactInternetSales", "CustomerKey", "DimCustomer", "CustomerKey", False),
    ("FactInternetSales", "PromotionKey", "DimPromotion", "PromotionKey", False),
    ("FactInternetSales", "CurrencyKey", "DimCurrency", "CurrencyKey", False),
    ("FactInternetSales", "SalesTerritoryKey", "DimSalesTerritory", "SalesTerritoryKey", False),

    ("FactResellerSales", "ProductKey", "DimProduct", "ProductKey", False),
    ("FactResellerSales", "OrderDateKey", "DimDate", "DateKey", False),
    ("FactResellerSales", "DueDateKey", "DimDate", "DateKey", False),
    ("FactResellerSales", "ShipDateKey", "DimDate", "DateKey", False),
    ("FactResellerSales", "ResellerKey", "DimReseller", "ResellerKey", False),
    ("FactResellerSales", "EmployeeKey", "DimEmployee", "EmployeeKey", False),
    ("FactResellerSales", "PromotionKey", "DimPromotion", "PromotionKey", False),
    ("FactResellerSales", "CurrencyKey", "DimCurrency", "CurrencyKey", False),
    ("FactResellerSales", "SalesTerritoryKey", "DimSalesTerritory", "SalesTerritoryKey", False),

    ("FactProductInventory", "ProductKey", "DimProduct", "ProductKey", False),
    ("FactProductInventory", "DateKey", "DimDate", "DateKey", False),
]

NULL_TOKENS = {"", "NULL", r"\N"}


def rows_for(table: str):
    path = RAW_DIR / f"{table}.csv"
    columns = SCHEMAS[table]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="|")
        for line_number, row in enumerate(reader, start=1):
            if row and row[-1] == "":
                row = row[:-1]
            if len(row) != len(columns):
                yield line_number, None
                continue
            yield line_number, dict(zip(columns, row))


def normalize(value: str) -> str | None:
    value = value.strip()
    return None if value in NULL_TOKENS else value


def write_dictionary() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / "source-data-dictionary.csv"

    fk_lookup = {
        (child_table, child_col): f"{parent_table}.{parent_col}"
        for child_table, child_col, parent_table, parent_col, _ in FOREIGN_KEYS
    }

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "ordinal", "column", "key_role", "references"])

        for table, columns in SCHEMAS.items():
            pk_columns = set(PRIMARY_KEYS.get(table, ()))
            for ordinal, column in enumerate(columns, start=1):
                roles: list[str] = []
                if column in pk_columns:
                    roles.append("PK")
                if (table, column) in fk_lookup:
                    roles.append("FK")
                writer.writerow([
                    table,
                    ordinal,
                    column,
                    "+".join(roles) if roles else "attribute/measure",
                    fk_lookup.get((table, column), ""),
                ])


def main() -> None:
    missing = [table for table in SCHEMAS if not (RAW_DIR / f"{table}.csv").exists()]
    if missing:
        raise SystemExit(
            "Missing required raw files:\n- "
            + "\n- ".join(missing)
            + "\n\nRun: .\\scripts\\download_adventureworks.ps1 -IncludeFacts"
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    write_dictionary()

    table_report: list[dict[str, object]] = []
    primary_key_sets: dict[str, set[tuple[str, ...]]] = {}

    print("\n[1/2] Validating row widths and primary/grain keys...")

    for table in SCHEMAS:
        pk_columns = PRIMARY_KEYS[table]
        seen: set[tuple[str, ...]] = set()
        row_count = 0
        malformed_rows = 0
        null_pk_rows = 0
        duplicate_pk_rows = 0

        for _, row in rows_for(table):
            row_count += 1
            if row is None:
                malformed_rows += 1
                continue

            key = tuple(normalize(row[col]) for col in pk_columns)
            if any(value is None for value in key):
                null_pk_rows += 1
                continue

            if key in seen:
                duplicate_pk_rows += 1
            else:
                seen.add(key)

        primary_key_sets[table] = seen
        table_report.append({
            "table": table,
            "rows": row_count,
            "expected_columns": len(SCHEMAS[table]),
            "malformed_rows": malformed_rows,
            "null_pk_rows": null_pk_rows,
            "duplicate_pk_rows": duplicate_pk_rows,
            "status": "PASS" if not (malformed_rows or null_pk_rows or duplicate_pk_rows) else "FAIL",
        })

    table_report_path = REPORT_DIR / "table-integrity-report.csv"
    with table_report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=table_report[0].keys())
        writer.writeheader()
        writer.writerows(table_report)

    print("[2/2] Validating foreign keys...")

    fk_report: list[dict[str, object]] = []

    for child_table, child_col, parent_table, parent_col, nullable in FOREIGN_KEYS:
        parent_keys = primary_key_sets[parent_table]
        orphan_count = 0
        null_count = 0
        checked_rows = 0
        orphan_examples: Counter[str] = Counter()

        for _, row in rows_for(child_table):
            if row is None:
                continue

            checked_rows += 1
            value = normalize(row[child_col])

            if value is None:
                null_count += 1
                continue

            if (value,) not in parent_keys:
                orphan_count += 1
                orphan_examples[value] += 1

        status = "PASS"
        if orphan_count > 0 or (null_count > 0 and not nullable):
            status = "FAIL"

        fk_report.append({
            "child_table": child_table,
            "child_column": child_col,
            "parent_table": parent_table,
            "parent_column": parent_col,
            "checked_rows": checked_rows,
            "null_values": null_count,
            "orphan_rows": orphan_count,
            "nullable": nullable,
            "status": status,
            "orphan_examples": ";".join(key for key, _ in orphan_examples.most_common(5)),
        })

    fk_report_path = REPORT_DIR / "foreign-key-report.csv"
    with fk_report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fk_report[0].keys())
        writer.writeheader()
        writer.writerows(fk_report)

    print("\nTable / grain checks")
    print("-" * 92)
    print(f"{'Table':28} {'Rows':>10} {'Bad':>7} {'NullPK':>8} {'DupPK':>8} {'Status':>8}")
    print("-" * 92)
    for item in table_report:
        print(
            f"{item['table']:28} "
            f"{item['rows']:>10,} "
            f"{item['malformed_rows']:>7,} "
            f"{item['null_pk_rows']:>8,} "
            f"{item['duplicate_pk_rows']:>8,} "
            f"{item['status']:>8}"
        )

    failed_fks = [item for item in fk_report if item["status"] == "FAIL"]

    print("\nForeign-key checks")
    print("-" * 92)
    print(f"Checks: {len(fk_report)} | Failed: {len(failed_fks)}")
    for item in failed_fks:
        print(
            f"FAIL {item['child_table']}.{item['child_column']} -> "
            f"{item['parent_table']}.{item['parent_column']} | "
            f"orphans={item['orphan_rows']} nulls={item['null_values']}"
        )

    print("\nGenerated:")
    print(f"- {REPORT_DIR / 'source-data-dictionary.csv'}")
    print(f"- {table_report_path}")
    print(f"- {fk_report_path}")

    failed_tables = [item for item in table_report if item["status"] == "FAIL"]
    if failed_tables or failed_fks:
        raise SystemExit("\nIntegrity validation completed with failures. Review the generated reports.")

    print("\nIntegrity validation PASSED.")


if __name__ == "__main__":
    main()
