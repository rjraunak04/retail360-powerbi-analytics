# Retail360 — Row-Level Security Design

## Objective

Stage 8 adds a reproducible territory-based RLS demonstration for the report's sales domain without pretending that the model contains a full enterprise identity-to-territory entitlement system.

## Implemented roles

| Role | Sales territory filter | Inventory access |
|---|---|---|
| `RLS_North_America` | `DimSalesTerritory[Territory Group] = "North America"` | denied |
| `RLS_Europe` | `DimSalesTerritory[Territory Group] = "Europe"` | denied |
| `RLS_Pacific` | `DimSalesTerritory[Territory Group] = "Pacific"` | denied |

The roles use `modelPermission: read`. Role membership is intentionally not hard-coded in source control; users/groups are assigned in the Power BI Service or deployment environment.

## Why inventory is denied for regional roles

`FactInventory` is Product × Date snapshot data and has no sales-territory key. Returning global inventory to a regional sales role would leak data outside the role's intended scope. Each regional role therefore applies:

`tablePermission FactInventory = FALSE()`

This makes territory-restricted inventory KPIs blank/zero rather than silently returning global inventory.

## Filter propagation

The territory filter is placed on `DimSalesTerritory`. The existing one-to-many relationship propagates the security filter to `FactSales`. No bidirectional relationships are introduced.

Other dimensions remain structurally unchanged. Regional report visuals are expected to be measure-driven so sales measures are evaluated through the secured fact table.

## Production extension

For a production deployment with many users, replace the three static demonstration roles with a governed user-to-territory entitlement bridge keyed by Microsoft Entra UPN/group membership. Keep identity assignments outside the PBIP repository.

## Validation

Stage 8 validates that:

- exactly three regional roles are registered in `model.tmdl`
- each role has read permission
- each role filters only its intended territory group
- regional roles deny `FactInventory`
- no user or group identities are committed to source control
- relationship direction remains single-direction and no new security-bidirectional relationship is introduced
- SQL baselines reconcile territory totals back to global sales


## Local automated RLS runtime validation

The three TMDL role definitions are validated structurally in source control. For local automated runtime QA, the Stage 8 DAX queries apply the exact same territory filter expression explicitly and compare the resulting sales lines, orders and sales value with SQL-derived baselines. They also apply the same fail-closed inventory semantics used by the role.

The verifier intentionally does **not** pass `Roles=<role>` to the local Power BI Desktop Analysis Services endpoint. Role impersonation through Analysis Services connection properties requires administrative permissions; a normal Desktop external connection can be rejected even though the model and role are valid.

Actual identity/role behavior is therefore validated interactively with **Modeling → View As** in Power BI Desktop or **Test as role** after deployment to Power BI Service. The automated local gate verifies the source-controlled role definition and the equivalent filter semantics without pretending to impersonate an administrator.
