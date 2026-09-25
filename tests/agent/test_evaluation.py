from agent.evaluation import evaluate, load_benchmark


def test_benchmark_has_minimum_coverage():
    cases = load_benchmark()
    assert len(cases) >= 20
    assert {"kpi_lookup", "semantic_lookup", "discovery"} <= {case["expected_intent"] for case in cases}


def test_benchmark_ids_are_unique():
    cases = load_benchmark()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))


def test_agent_meets_day6_quality_gate():
    report = evaluate()
    assert report.total >= 20
    assert report.pass_rate >= 0.95
    assert report.intent_accuracy >= 0.95
    assert report.tool_accuracy == 1.0
    assert report.grounding_accuracy == 1.0
    assert report.answer_accuracy >= 0.95
