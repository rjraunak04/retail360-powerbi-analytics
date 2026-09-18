# Stage 5 — Power BI Semantic Model

## Objective

Build a source-controlled semantic-model definition on top of the governed PostgreSQL `analytics` schema.

## Connectivity decision

Retail360 uses the native Power Query PostgreSQL connector in **Import** mode for the portfolio model.

Connection parameters:

- `pServer` — default local value: `localhost:5432`
- `pDatabase` — default: `retail360`

Credentials are intentionally not stored in source control.

## Model tables

### Dimensions

- DimDate
- DimProduct
- DimCustomer
- DimReseller
- DimEmployee
- DimGeography
- DimSalesTerritory
- DimPromotion
- DimCurrency
- DimChannel

### Facts

- FactSales
- FactInventory

Power BI is connected only to the PostgreSQL `analytics` schema. The report model does not connect directly to raw or staging objects.

## Relationship policy

All fact-to-dimension relationships are many-to-one from the fact side and single-direction from dimensions to facts.

Date roles:

- FactSales[Order Date Key] → DimDate[Date Key] — active
- FactSales[Due Date Key] → DimDate[Date Key] — inactive
- FactSales[Ship Date Key] → DimDate[Date Key] — inactive
- FactInventory[Date Key] → DimDate[Date Key] — active

Due/Ship analysis will use `USERELATIONSHIP` measures in Stage 6.

## Field visibility

Technical warehouse keys are hidden from report consumers.

Fact additive columns are also hidden from the normal report field list so report authors use governed DAX measures rather than implicit aggregations.

Business-facing descriptive columns remain visible.

## Date model

DimDate[Date] is the canonical model date column.

Because the warehouse relationships use integer surrogate date keys, the Desktop model should mark DimDate as the model Date table using the Date column before classic DAX time-intelligence measures are authored.

## Repository artifacts

- `powerbi/semantic-model-contract.json` — machine-readable semantic contract
- `powerbi/tmdl/stage5_semantic_model.tmdl` — fast-path TMDL model bootstrap
- `power-query/*.m` — one parameterized PostgreSQL query per model table
- `dax/qa/stage5_model_qa.dax` — post-load Desktop QA queries
- `scripts/validate_semantic_model.py` — repository-level semantic contract validation

## Power BI Desktop materialization

The repository definition is source-controlled, but Power BI Desktop is required to materialize and credential the local model.

Fast path:

1. Start the local PostgreSQL `retail360` database.
2. Open a blank Power BI Desktop report.
3. Open **Model > TMDL view**.
4. Apply `powerbi/tmdl/stage5_semantic_model.tmdl`.
5. Supply PostgreSQL credentials when prompted.
6. Refresh.
7. Mark `DimDate[Date]` as the Date table.
8. Run `dax/qa/stage5_model_qa.dax` in DAX Query View.
9. Save the project as PBIP using TMDL format so Desktop becomes the serializer of record.

## Stage 5 exit gate

Repository gate:

- 12 semantic tables defined
- 14 relationships defined
- only Order Date active for FactSales date role
- technical keys hidden
- PostgreSQL sources parameterized
- semantic contract validation passes

Desktop gate:

- model refresh succeeds
- expected row counts match
- date table marked
- relationships appear exactly as documented
- PBIP is saved by Power BI Desktop
