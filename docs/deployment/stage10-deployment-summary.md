# Retail360 — Stage 10 Deployment Summary

## Status

**Stage 10 — COMPLETE (portfolio/fallback deployment path)**

Retail360 is deployment-ready as a source-controlled PBIP project and as a reproducible local portfolio release package.

The repository does **not** claim that a Power BI Service workspace publication, gateway binding, scheduled refresh, or tenant role membership has been completed. Those actions require an authenticated Power BI tenant/workspace and environment-specific credentials.

## Completed deployment deliverables

- canonical PBIP artifact: `powerbi/Retail360.pbip`
- source-controlled PBIR report and TMDL semantic model
- PostgreSQL refresh/deployment guidance
- PBIP/PBIX distribution strategy
- Power BI Service publication checklist
- versioned release manifest
- one-command Windows release packaging helper
- SHA-256 checksum generation for packaged files
- recruiter-ready dashboard screenshots
- reproducible local setup
- CI-enforced Stage 10 deployment contract
- GitHub Actions build of the versioned release ZIP
- short-lived CI artifact containing the release ZIP, release metadata and SHA-256 checksum manifest

## Deployment mode

The completed portfolio deployment path is:

```text
Git-reviewed source
      |
      v
Canonical PBIP / PBIR / TMDL
      |
      v
Versioned portfolio release package
      |
      +--> Local Power BI Desktop demo
      |
      +--> Recruiter / interviewer distribution
      |
      +--> Power BI Service publish when tenant access is available
```

The package is generated locally under `dist/` and is intentionally not committed. GitHub Actions also builds the same package during Stage 10 validation and uploads a short-lived workflow artifact for review.

## Build the release package

From the repository root on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package_stage10_release.ps1
```

The helper creates:

```text
dist/
  Retail360-1.0.0-portfolio/
  Retail360-1.0.0-portfolio.zip
```

The unpacked folder contains the canonical Power BI project, SQL/Python/Power Query source, documentation, screenshots, deployment guidance, and a `SHA256SUMS.txt` integrity file.

## Power BI Service readiness

Retail360 uses Import mode and parameterized PostgreSQL connection settings.

For Power BI Service refresh, one of these environment patterns is required:

1. local/private PostgreSQL + on-premises data gateway
2. reachable cloud/private-network PostgreSQL + configured Service connection

After publication, the semantic-model owner must configure environment-specific credentials, refresh schedule, gateway/connection mapping, and RLS membership.

See `docs/deployment/powerbi-service-publish-checklist.md`.

## Security boundary

The deployment package excludes or ignores:

- `.env`
- credentials/secrets files
- Power BI `.pbi` local caches
- `.runtime`
- virtual environments
- raw local data
- generated `dist/` output

No password, gateway recovery key, tenant secret, or user-specific connection token belongs in Git.

## Stage 10 exit gate

Stage 10 fallback deployment is complete when all of the following pass:

- Stage 9 recruiter package is present
- canonical PBIP exists
- all 10 report screenshots exist
- deployment documentation exists
- release manifest is valid
- packaging script is syntactically valid
- repository ignores generated distribution output
- CI Stage 10 deployment validation passes
- documentation does not falsely claim Power BI Service publication

Power BI Service publication remains an optional environment step, not a fabricated repository claim.
