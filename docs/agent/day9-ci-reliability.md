# Day 9 - CI, Reliability and Regression Protection

Day 9 makes the agent layer continuously verifiable.

## Dedicated GitHub Actions workflow

Agent changes now trigger a focused Agent Quality CI workflow on pull requests to main/develop and pushes to main/develop. Path filters avoid running the agent pipeline for unrelated repository changes.

The workflow:

1. checks out the repository
2. installs Python 3.12 and dependencies
3. compiles the agent package
4. runs all agent tests
5. runs the deterministic benchmark
6. writes machine-readable evaluation evidence
7. enforces quality thresholds
8. uploads the evaluation report as a CI artifact

## Quality thresholds

CI requires:

- at least 20 evaluated benchmark cases
- overall pass rate >= 95%
- intent accuracy >= 95%
- tool-routing accuracy = 100%
- KPI-grounding accuracy = 100%
- answer-evidence accuracy >= 95%

## Reliability controls

The workflow has read-only repository permissions, a 10-minute job timeout, pip caching, concurrency cancellation for superseded runs, and a 14-day evaluation artifact.

## Regression protection

A planner, KPI dictionary, semantic-contract or agent-code change can no longer silently reduce measured quality. The CI validator fails the workflow when metrics fall below the agreed baseline.

The validator itself is covered by tests, including deliberate metric regressions and insufficient benchmark coverage.

## Separation from warehouse CI

Agent Quality CI is intentionally separate from the heavier PostgreSQL Warehouse CI. This gives fast feedback for agent-only changes while preserving the existing end-to-end warehouse validation pipeline.
