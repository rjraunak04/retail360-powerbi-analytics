import json

import pytest

from scripts.validate_agent_evaluation import MINIMUMS, validate


def write_report(tmp_path, **overrides):
    report = {
        "total": 20,
        "pass_rate": 1.0,
        "intent_accuracy": 1.0,
        "tool_accuracy": 1.0,
        "grounding_accuracy": 1.0,
        "answer_accuracy": 1.0,
        "cases": [],
    }
    report.update(overrides)
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def test_ci_quality_gate_accepts_healthy_report(tmp_path):
    validate(write_report(tmp_path))


@pytest.mark.parametrize("metric", list(MINIMUMS))
def test_ci_quality_gate_rejects_metric_regression(tmp_path, metric):
    path = write_report(tmp_path, **{metric: MINIMUMS[metric] - 0.01})
    with pytest.raises(SystemExit):
        validate(path)


def test_ci_quality_gate_requires_benchmark_coverage(tmp_path):
    with pytest.raises(SystemExit):
        validate(write_report(tmp_path, total=19))
