# Retail360 — Stage 5 Semantic Model Validation

## Status

**Repository validation PASSED — 18 September 2026**

The Power BI semantic-model definition is now source controlled and validated as a contract against the governed PostgreSQL analytics layer.

## Repository validation results

- semantic tables: **12/12 PASS**
- relationships: **14/14 PASS**
- storage mode: **Import**
- canonical date table: **DimDate[Date]**
- FactSales active date relationship: **Order Date only**
- Due Date relationship: **inactive**
- Ship Date relationship: **inactive**
- Power Query analytics sources: **12/12 parameterized**
- Power Query connection parameters: **2/2 present**
- TMDL structural contract: **PASS**

## Model architecture

Dimensions:

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

Facts:

- FactSales
- FactInventory

Technical keys and raw additive fact columns are hidden from normal report consumption so Stage 6 can expose governed DAX measures instead of relying on implicit aggregations.

## PostgreSQL connection design

The model uses the native Power Query PostgreSQL connector with two source-controlled parameters:

- `pServer`
- `pDatabase`

Credentials are intentionally excluded from Git.

## Source-control artifacts

- `powerbi/semantic-model-contract.json`
- `powerbi/tmdl/stage5_semantic_model.tmdl`
- `power-query/pServer.m`
- `power-query/pDatabase.m`
- 12 table-specific Power Query M files
- `dax/qa/stage5_model_qa.dax`
- `scripts/validate_semantic_model.py`
- semantic model and relationship documentation

## Desktop materialization gate

Power BI Desktop itself is not available in the repository CI runner. Therefore the final runtime gate is intentionally separate from repository validation.

The local Desktop gate is:

1. local `retail360` PostgreSQL instance is running
2. TMDL script is applied in Power BI Desktop
3. PostgreSQL credentials are supplied locally
4. model refresh succeeds
5. DimDate is confirmed as the Date table
6. DAX QA query returns expected row counts
7. Desktop saves the model as PBIP/TMDL

The repository-side Stage 5 definition is approved for Stage 6 DAX development while this one-time local materialization is completed.
