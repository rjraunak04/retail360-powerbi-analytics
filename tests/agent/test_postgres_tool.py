import pytest

from agent import AgentConfig
from agent.tools.postgres import (
    PostgresAnalyticsTool,
    QueryRejected,
    validate_read_only_query,
)


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM analytics.fact_sales",
        "UPDATE analytics.fact_sales SET sales_amount = 0",
        "DROP TABLE analytics.fact_sales",
        "SELECT 1; SELECT 2",
        "SELECT * FROM raw.fact_sales",
    ],
)
def test_unsafe_queries_are_rejected(query):
    with pytest.raises(QueryRejected):
        validate_read_only_query(query)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM analytics.fact_sales",
        "WITH x AS (SELECT 1 AS value) SELECT * FROM x",
        "SELECT COUNT(*) AS rows FROM analytics.fact_sales;",
    ],
)
def test_read_only_queries_are_accepted(query):
    assert validate_read_only_query(query)


class FakeCursor:
    description = (("product",), ("sales",))

    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query):
        self.executed.append(str(query))

    def fetchmany(self, size):
        return [("Road Bike", 100.0), ("Helmet", 50.0)]


class FakeConnection:
    def __init__(self):
        self.read_only = False
        self.cursor_instance = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return self.cursor_instance


def test_tool_enforces_read_only_and_returns_normalized_rows():
    connection = FakeConnection()
    tool = PostgresAnalyticsTool(
        config=AgentConfig(max_rows=10),
        connection_factory=lambda: connection,
    )

    result = tool.run(query="SELECT * FROM analytics.fact_sales")

    assert result.ok is True
    assert connection.read_only is True
    assert result.data == [
        {"product": "Road Bike", "sales": 100.0},
        {"product": "Helmet", "sales": 50.0},
    ]
    assert result.metadata["read_only"] is True


def test_tool_rejects_before_connecting():
    connected = False

    def connect():
        nonlocal connected
        connected = True
        return FakeConnection()

    result = PostgresAnalyticsTool(connection_factory=connect).run(
        query="TRUNCATE analytics.fact_sales"
    )

    assert result.ok is False
    assert result.metadata["rejected"] is True
    assert connected is False
