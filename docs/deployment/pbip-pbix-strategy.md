# Retail360 — PBIP / PBIX Strategy

## Canonical artifact

`powerbi/Retail360.pbip` and its PBIR/TMDL folders are the canonical source-controlled development artifacts.

Why PBIP is canonical:

- semantic-model and report definitions are diffable
- DAX, relationships, roles and report metadata can be code-reviewed
- Git branches and CI can validate structural contracts
- binary merge conflicts are avoided

## PBIX use

A PBIX is a distribution/demo artifact, not the canonical source.

Use PBIX when:

- a recruiter/interviewer wants a single file
- a local backup is needed before a Desktop upgrade
- a Power BI Service publish workflow requires it

Do not replace the PBIP source tree with a PBIX-only workflow.

## Source-control policy

Commit:

- PBIP shortcut
- PBIR report definition
- TMDL semantic model
- DAX QA queries
- validation scripts
- documentation

Do not commit:

- credentials
- gateway secrets
- local `.pbi` caches
- temporary Performance Analyzer exports
- runtime proof scratch files
- machine-specific workspace files

## Release strategy

For a portfolio release:

1. tag the reviewed Git commit
2. publish/deploy from the canonical PBIP model
3. optionally attach an exported PBIX outside the Git source tree
4. capture dashboard screenshots and deployment evidence for Stage 9/10
