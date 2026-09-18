# Retail360 — Power BI Relationship Matrix

| From | To | Cardinality | Active | Filter direction |
|---|---|---|---|---|
| FactSales[Channel Key] | DimChannel[Channel Key] | *:1 | Yes | Dim → Fact |
| FactSales[Product Key] | DimProduct[Product Key] | *:1 | Yes | Dim → Fact |
| FactSales[Order Date Key] | DimDate[Date Key] | *:1 | Yes | Dim → Fact |
| FactSales[Due Date Key] | DimDate[Date Key] | *:1 | No | Dim → Fact |
| FactSales[Ship Date Key] | DimDate[Date Key] | *:1 | No | Dim → Fact |
| FactSales[Customer Key] | DimCustomer[Customer Key] | *:1 | Yes | Dim → Fact |
| FactSales[Reseller Key] | DimReseller[Reseller Key] | *:1 | Yes | Dim → Fact |
| FactSales[Employee Key] | DimEmployee[Employee Key] | *:1 | Yes | Dim → Fact |
| FactSales[Promotion Key] | DimPromotion[Promotion Key] | *:1 | Yes | Dim → Fact |
| FactSales[Currency Key] | DimCurrency[Currency Key] | *:1 | Yes | Dim → Fact |
| FactSales[Sales Territory Key] | DimSalesTerritory[Sales Territory Key] | *:1 | Yes | Dim → Fact |
| FactSales[Geography Key] | DimGeography[Geography Key] | *:1 | Yes | Dim → Fact |
| FactInventory[Product Key] | DimProduct[Product Key] | *:1 | Yes | Dim → Fact |
| FactInventory[Date Key] | DimDate[Date Key] | *:1 | Yes | Dim → Fact |

No bidirectional or many-to-many relationships are part of the Stage 5 semantic model.
