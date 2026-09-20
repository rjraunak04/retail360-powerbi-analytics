# Retail360 — Power BI Service Publish Checklist

Use this checklist when an authenticated Power BI tenant/workspace is available.

## 1. Pre-publish gate

Before publishing:

- use the reviewed `develop`/release commit
- confirm `powerbi/Retail360.pbip` opens in Power BI Desktop
- confirm the semantic model refreshes successfully
- confirm Stage 6/8 runtime evidence remains valid
- do not embed passwords or personal credentials in the project

## 2. Choose the PostgreSQL connectivity pattern

Retail360 is an Import-mode semantic model.

### Pattern A — local/private PostgreSQL

Use an on-premises data gateway.

- install/configure the gateway on a machine that can reach PostgreSQL
- create the PostgreSQL data-source/connection mapping
- map `pServer` and `pDatabase` to the target environment
- configure credentials in Power BI Service, not in Git

### Pattern B — reachable hosted PostgreSQL

Use an approved PostgreSQL endpoint reachable from the Service environment.

- update environment-specific connection parameters
- configure credentials in the semantic-model connection settings
- keep network/firewall/TLS policy outside source control

## 3. Publish

From Power BI Desktop:

1. Open the canonical Retail360 project.
2. Refresh successfully.
3. Use **Publish** and select the intended workspace.
4. Confirm the report and semantic model appear in that workspace.

Do not publish from an unreviewed local copy.

## 4. Configure semantic-model settings

In the target workspace:

- verify data-source/connection mapping
- configure credentials
- configure gateway mapping when Pattern A is used
- set a refresh schedule only after an on-demand refresh succeeds
- confirm the semantic model owner is correct

## 5. Validate refreshed values

After a successful Service refresh, reconcile at minimum:

| KPI | Expected |
|---|---:|
| Total Sales | 109,809,274.2030 |
| Total Product Cost | 97,257,907.9547 |
| Gross Profit | 12,551,366.2483 |
| Units Sold | 274,776 |
| Distinct Orders | 31,455 |
| Internet Sales | 29,358,677.2207 |
| Reseller Sales | 80,450,596.9823 |
| Current Inventory Value | 23,603,975.5700 |
| Current Inventory Units | 258,981 |

A materially different value requires refresh/source investigation before release.

## 6. Configure RLS membership

The model contains demonstration roles:

- `RLS_North_America`
- `RLS_Europe`
- `RLS_Pacific`

Role definitions are source-controlled. User/group membership is environment-specific and must be assigned in Power BI Service.

Use **Test as role** / equivalent Service validation before sharing.

## 7. Sharing and distribution

For a portfolio/recruiter deployment:

- prefer workspace/app/report access appropriate to the tenant
- do not expose a public link containing private or licensed data
- AdventureWorks sample data is suitable for demonstration, but tenant policy still applies
- keep GitHub source and deployment environment credentials separate

## 8. Evidence to capture

If Service publication is completed later, capture:

- workspace/report screenshot
- successful refresh-history screenshot
- RLS role-test screenshot
- deployment date
- reviewed Git commit SHA

Do not commit access tokens, tenant secrets, gateway keys, private workspace IDs when they are sensitive.

## Current repository claim

The repository is **Power BI Service ready**, but does not claim that Service publication has occurred until the above tenant-specific evidence exists.
