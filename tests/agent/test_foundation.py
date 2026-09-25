from agent import AgentConfig, AnalyticsAgent
from agent.tools import ToolResult


class EchoTool:
    name = "echo"
    description = "Echo a value for contract testing."

    def run(self, **kwargs):
        return ToolResult(tool_name=self.name, ok=True, data=kwargs)


def test_safe_defaults():
    config = AgentConfig()
    assert config.require_read_only is True
    assert config.allowed_schema == "analytics"
    assert config.max_rows == 100


def test_tool_registration_and_execution():
    agent = AnalyticsAgent()
    agent.register_tool(EchoTool())

    result = agent.run_tool("echo", value="Retail360")

    assert agent.tool_names == ("echo",)
    assert result.ok is True
    assert result.data["value"] == "Retail360"


def test_empty_question_is_rejected():
    agent = AnalyticsAgent()

    try:
        agent.answer("   ")
    except ValueError as exc:
        assert "Question" in str(exc)
    else:
        raise AssertionError("Expected empty question to be rejected")
