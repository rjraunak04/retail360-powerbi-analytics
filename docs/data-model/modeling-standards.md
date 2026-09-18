# Retail360 — Data Modelling Standards

## Modelling Approach

Retail360 will use a dimensional star-schema architecture.

## Core Rules

1. Each fact table must have a clearly defined grain.
2. Dimensions should contain descriptive business attributes.
3. Relationships should primarily be one-to-many.
4. Dimension filters should flow toward fact tables.
5. Many-to-many relationships should be avoided unless justified.
6. Business measures should be implemented using explicit DAX measures.
7. Technical identifiers should be hidden from report consumers.
8. Date intelligence should use a dedicated Date dimension.
9. Raw-source transformations should not be mixed with presentation logic.
10. KPI definitions must be documented and validated before dashboard use.

## Naming Convention

### Dimensions

DimDate  
DimProduct  
DimStore  
DimCustomer  
DimGeography  
DimPromotion

### Facts

FactSales  
FactInventory  
FactPromotion

### Measures

Readable business names should be used:

Total Sales  
Gross Profit  
Gross Margin %  
Sales YoY %  
Average Order Value