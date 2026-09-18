# Retail360 — Stage 2 PostgreSQL Validation

## Status

**PASSED — 18 September 2026**

Stage 2 was executed end to end in GitHub Actions against PostgreSQL 16.

## Validated flow

Microsoft AdventureWorksDW source download  
→ source-integrity validation  
→ PostgreSQL database creation  
→ raw/staging/analytics/audit schema creation  
→ 14-table raw ingestion  
→ audit metadata capture  
→ expected-vs-actual row reconciliation

## Results

- PostgreSQL version family: 16
- source files: 14
- source-integrity checks: PASS
- foreign-key checks: 25/25 PASS
- raw tables loaded: 14
- total rows loaded: 922,106
- row reconciliation: 14/14 PASS
- audited load status: SUCCESS

## Core fact row counts

| Table | Rows | Status |
|---|---:|---|
| raw.fact_internet_sales | 60,398 | PASS |
| raw.fact_reseller_sales | 60,855 | PASS |
| raw.fact_product_inventory | 776,286 | PASS |

## Compatibility normalization

The source contains embedded NUL bytes in some product text attributes. PostgreSQL `text` cannot store NUL bytes.

Retail360 applies a deterministic compatibility rule during landing:

- binary/image fields use `bytea`
- embedded NUL bytes in ordinary text fields are removed
- the number removed is written to the audit layer

The validated run normalized **574 NUL bytes in DimProduct** and zero in the other scoped tables.

This does not change source row counts, fact grains, primary-key checks, or referential-integrity results.

## Stage 2 exit decision

The PostgreSQL warehouse foundation is approved for downstream staging and business transformation.

Next: **Stage 3 — Staging and Business Transformation**.
