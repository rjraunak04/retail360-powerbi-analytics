"""Validate Retail360 agent evaluation metrics for CI."""

import json
import sys
from pathlib import Path

MINIMUMS = {
    "pass_rate": 0.95,
    "intent_accuracy": 0.95,
    "tool_accuracy": 1.0,
    "grounding_accuracy": 1.0,
    "answer_accuracy": 0.95,
}


def validate(path: Path) -> None:
    report = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    if report.get("total", 0) < 20:
        problems.append("at least 20 evaluated cases are required")
    for metric, minimum in MINIMUMS.items():
        value = float(report.get(metric, 0.0))
        if value < minimum:
            problems.append(f"{metric} below required threshold")
    if problems:
        raise SystemExit("Agent quality gate failed: " + "; ".join(problems))
    print("Agent quality gate PASS")


if __name__ == "__main__":
    validate(Path(sys.argv[1]))
