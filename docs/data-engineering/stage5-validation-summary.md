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


## Final Power BI Desktop runtime proof

**Status: PASSED — 19 September 2026**

The Retail360 PBIP project was opened in Power BI Desktop against the local PostgreSQL analytics database and verified through the live local semantic-model engine.

Runtime connection:

- local Power BI Analysis Services port discovered successfully
- semantic model catalog discovered successfully
- final DAX QA executed directly against the loaded model
- proof result: **20/20 checks PASS**

Validated results:

| Check | Actual | Expected | Status |
|---|---:|---:|---|
| DimChannel rows | 3 | 3 | PASS |
| DimCurrency rows | 106 | 106 | PASS |
| DimCustomer rows | 18,485 | 18,485 | PASS |
| DimDate rows | 3,652 | 3,652 | PASS |
| DimEmployee rows | 297 | 297 | PASS |
| DimGeography rows | 656 | 656 | PASS |
| DimProduct rows | 607 | 607 | PASS |
| DimPromotion rows | 17 | 17 | PASS |
| DimReseller rows | 702 | 702 | PASS |
| DimSalesTerritory rows | 12 | 12 | PASS |
| Distinct Orders | 31,455 | 31,455 | PASS |
| FactInventory rows | 776,286 | 776,286 | PASS |
| FactSales rows | 121,253 | 121,253 | PASS |
| Gross Profit | 12,551,366.2483 | 12,551,366.2483 | PASS |
| Internet sales lines | 60,398 | 60,398 | PASS |
| Inventory Value (all snapshots) | 29,713,024,789.83 | 29,713,024,789.83 | PASS |
| Reseller sales lines | 60,855 | 60,855 | PASS |
| Total Product Cost | 97,257,907.9547 | 97,257,907.9547 | PASS |
| Total Sales | 109,809,274.203 | 109,809,274.203 | PASS |
| Units Sold | 274,776 | 274,776 | PASS |

The runtime verifier is available at:

`scripts/verify_powerbi_stage5_runtime.ps1`

The generated local evidence file is:

`docs/data-engineering/stage5-powerbi-runtime-proof.csv`

### Stage 5 decision

**Stage 5 — Power BI Semantic Model: COMPLETE**

All repository, CI, PostgreSQL, PBIP/TMDL, credential, refresh, and live Power BI semantic-model runtime gates have passed.
