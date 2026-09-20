# Retail360 — Power BI Refresh and Deployment Notes

## Current development topology

Retail360 uses Import mode. The PBIP semantic model connects to PostgreSQL through the parameters:

- `pServer`
- `pDatabase`

The local development source is PostgreSQL exposed on loopback. Credentials are not stored in the repository.

## Local refresh

1. Start Docker Desktop.
2. Start the Retail360 PostgreSQL service with `docker compose up -d postgres`.
3. Confirm PostgreSQL health.
4. Open `powerbi/Retail360.pbip`.
5. Refresh the semantic model.

Use the least-privilege read-only database account for Power BI access.

## Power BI Service

A loopback/local PostgreSQL endpoint is not directly reachable from the Power BI Service. For scheduled refresh, use one of these deployment patterns:

- keep PostgreSQL on-prem/local and configure an on-premises data gateway
- deploy PostgreSQL to an approved reachable cloud/private network and update the model parameters

The dataset owner configures credentials and refresh schedule in the target environment. Secrets, passwords and gateway recovery keys must never be committed.

## Refresh order

The analytics warehouse must be current before the Power BI Import refresh:

source files → raw → staging → analytics → Power BI semantic model.

The repository CI validates the raw/staging/analytics transformations independently from Desktop refresh.

## Failure handling

If refresh fails:

- confirm PostgreSQL is healthy
- confirm `pServer` / `pDatabase`
- confirm credentials and gateway mapping
- run `scripts/qa_analytics.py`
- run `scripts/qa_stage6_kpis.py`
- run `scripts/qa_stage8_enterprise.py`
- only then troubleshoot Desktop/Service refresh

## Deployment boundary

This repository does not claim Fabric pipelines, Azure Data Factory or Synapse deployment. Stage 10 covers publication to Power BI Service where account capabilities permit.
