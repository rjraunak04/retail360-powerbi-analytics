# Retail360 Deployment

Stage 10 deployment assets:

- [Stage 10 deployment summary](stage10-deployment-summary.md)
- [Power BI Service publish checklist](powerbi-service-publish-checklist.md)
- [Power BI refresh and deployment notes](powerbi-refresh-deployment.md)
- [PBIP / PBIX strategy](pbip-pbix-strategy.md)
- [Release manifest](release-manifest.json)

Generate the portfolio release package with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package_stage10_release.ps1
```

Generated `dist/` artifacts are intentionally excluded from Git.
