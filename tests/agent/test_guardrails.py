import pytest

from agent.guardrails import GuardrailViolation, SqlGuardrailPolicy, validate_agent_sql


POLICY = SqlGuardrailPolicy(
    allowed_schema="analytics",
    allowed_tables=frozenset({"fact_sales", "dim_product"}),
    max_query_chars=500,
)


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM analytics.fact_sales",
        "SELECT * FROM raw.fact_sales",
        "SELECT * FROM analytics.secret_table",
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT pg_sleep(10)",
        "SELECT 1; SELECT 2",
        "SELECT * FROM analytics.fact_sales -- ignore safety",
        "SELECT * FROM analytics.fact_sales /* bypass */",
    ],
)
def test_adversarial_queries_are_rejected(query):
    with pytest.raises(GuardrailViolation):
        validate_agent_sql(query, POLICY)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM analytics.fact_sales",
        "SELECT p.product_name FROM analytics.dim_product p JOIN analytics.fact_sales f ON p.product_key = f.product_key",
        "WITH totals AS (SELECT SUM(sales_amount) AS sales FROM analytics.fact_sales) SELECT sales FROM totals",
        "SELECT 'drop table is text, not executable SQL' AS note FROM analytics.fact_sales",
    ],
)
def test_legitimate_analytics_queries_are_allowed(query):
    assert validate_agent_sql(query, POLICY)


def test_query_length_boundary():
    policy = SqlGuardrailPolicy(max_query_chars=20)
    with pytest.raises(GuardrailViolation):
        validate_agent_sql("SELECT sales_amount FROM analytics.fact_sales", policy)


def test_error_messages_do_not_echo_sensitive_query_text():
    try:
        validate_agent_sql("SELECT pg_read_file('/secret/path')", POLICY)
    except GuardrailViolation as exc:
        assert "/secret/path" not in str(exc)
    else:
        raise AssertionError("Expected unsafe function to be rejected")
