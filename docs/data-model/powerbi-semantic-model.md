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

Retail360 now includes a ready-to-open PBIP project, so manual TMDL copy/paste is no longer required.

Project entry point:

`powerbi/Retail360.pbip`

The PBIP links:

`Retail360.Report -> Retail360.SemanticModel`

The semantic model is already stored in source-controlled TMDL under:

`powerbi/Retail360.SemanticModel/definition/`

The local launcher `scripts/open_powerbi_stage5.ps1` starts/checks PostgreSQL, executes warehouse and semantic-model validation, validates the PBIP structure, and opens `Retail360.pbip`.

On the first model refresh, Power BI Desktop can request the local PostgreSQL credential. Credentials are intentionally kept outside Git and must remain in the local Power BI credential store.

After the first successful refresh, run `powerbi/Retail360.SemanticModel/DAXQueries/Stage5 Model QA.dax` in DAX Query View to confirm model row counts.

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
