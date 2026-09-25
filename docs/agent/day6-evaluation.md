# Day 6 - Agent Evaluation and Regression Quality Gate

Day 6 turns the agent from a demo into a measurable system.

## Benchmark

The repository now contains a version-controlled benchmark with 20 representative business questions covering:

- governed KPI routing
- KPI grounding
- semantic-model routing
- model discovery
- inventory snapshot semantics
- weighted margin semantics
- collision-safe distinct-order semantics

Each case declares expected intent, first tool, optional governed KPI, and answer evidence.

## Metrics

The evaluation harness reports:

- overall pass rate
- intent accuracy
- tool-routing accuracy
- KPI grounding accuracy
- answer-evidence accuracy
- per-case pass/fail details

## Quality gate

Automated tests require:

- at least 20 benchmark cases
- unique benchmark IDs
- coverage of KPI lookup, semantic lookup and discovery
- overall pass rate >= 95%
- intent accuracy >= 95%
- tool-routing accuracy = 100%
- KPI grounding accuracy = 100%
- answer-evidence accuracy >= 95%

The benchmark is deterministic and provider-neutral. Later LLM planners must meet or exceed this baseline rather than being judged only from hand-picked demos.

## Run locally

    python -m agent.evaluation.evaluate

or as part of the test suite:

    pytest tests/agent

## Evaluation philosophy

Correct SQL syntax is not enough for analytics. Retail360 separately evaluates routing, business-definition grounding and evidence in the final response. This makes regressions visible when planner behavior changes.
