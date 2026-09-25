"""Deterministic evaluation harness for Retail360 agent behavior."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..factory import build_default_agent

BENCHMARK = Path(__file__).with_name("benchmark.json")


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    intent_ok: bool
    tool_ok: bool
    kpi_ok: bool
    answer_ok: bool


@dataclass(frozen=True)
class EvaluationReport:
    total: int
    passed: int
    pass_rate: float
    intent_accuracy: float
    tool_accuracy: float
    grounding_accuracy: float
    answer_accuracy: float
    cases: tuple[CaseResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "cases": [asdict(case) for case in self.cases]}


def load_benchmark(path: Path = BENCHMARK) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(path: Path = BENCHMARK) -> EvaluationReport:
    agent = build_default_agent()
    results = []

    for case in load_benchmark(path):
        response = agent.answer(case["question"])
        intent_ok = response.intent == case["expected_intent"]
        tool_ok = bool(response.plan and response.plan.steps and response.plan.steps[0].tool_name == case["expected_tool"])
        expected_kpi = case.get("expected_kpi")
        kpi_ok = True
        if expected_kpi:
            first = response.tool_results[0] if response.tool_results else None
            kpi_ok = bool(first and first.ok and first.data and first.data[0].get("measure") == expected_kpi)
        answer_ok = all(fragment.casefold() in response.answer.casefold() for fragment in case.get("answer_contains", []))
        passed = intent_ok and tool_ok and kpi_ok and answer_ok
        results.append(CaseResult(case["id"], passed, intent_ok, tool_ok, kpi_ok, answer_ok))

    total = len(results)
    count = lambda attr: sum(bool(getattr(item, attr)) for item in results)
    return EvaluationReport(
        total=total,
        passed=count("passed"),
        pass_rate=count("passed") / total if total else 0.0,
        intent_accuracy=count("intent_ok") / total if total else 0.0,
        tool_accuracy=count("tool_ok") / total if total else 0.0,
        grounding_accuracy=count("kpi_ok") / total if total else 0.0,
        answer_accuracy=count("answer_ok") / total if total else 0.0,
        cases=tuple(results),
    )


if __name__ == "__main__":
    print(json.dumps(evaluate().to_dict(), indent=2))
