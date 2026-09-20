# Retail360 — Source Keys and Grain Validation

Retail360 validates source keys before loading the analytical model.

## Dimension primary keys

| Table | Primary key |
|---|---|
| DimCurrency | CurrencyKey |
| DimCustomer | CustomerKey |
| DimDate | DateKey |
| DimEmployee | EmployeeKey |
| DimGeography | GeographyKey |
| DimProduct | ProductKey |
| DimProductCategory | ProductCategoryKey |
| DimProductSubcategory | ProductSubcategoryKey |
| DimPromotion | PromotionKey |
| DimReseller | ResellerKey |
| DimSalesTerritory | SalesTerritoryKey |

## Fact grains

| Table | Validated candidate grain |
|---|---|
| FactInternetSales | SalesOrderNumber + SalesOrderLineNumber |
| FactResellerSales | SalesOrderNumber + SalesOrderLineNumber |
| FactProductInventory | ProductKey + DateKey |

## Important referential-integrity paths

- Product → Product Subcategory → Product Category
- Customer → Geography → Sales Territory
- Reseller → Geography → Sales Territory
- Employee → Sales Territory
- Internet Sales → Product, Date, Customer, Promotion, Currency, Territory
- Reseller Sales → Product, Date, Reseller, Employee, Promotion, Currency, Territory
- Product Inventory → Product, Date

## Run

After all dimensions and facts are downloaded:

```powershell
python .\scripts\validate_source_integrity.py
```

The validator generates:

- `docs/data-model/source-data-dictionary.csv`
- `docs/data-model/table-integrity-report.csv`
- `docs/data-model/foreign-key-report.csv`

A successful run requires:

- zero malformed rows
- zero null primary/grain keys
- zero duplicate primary/grain keys
- zero orphan foreign keys
- no nulls in non-nullable foreign keys

These checks establish the trustworthy source layer before PostgreSQL ingestion.
