"""Factory for a locally grounded Retail360 analytics agent."""

from .config import AgentConfig
from .orchestrator import AnalyticsAgent
from .tools import KpiMetadataTool, PostgresAnalyticsTool, SemanticMetadataTool


def build_default_agent(
    config: AgentConfig | None = None,
    include_database: bool = False,
) -> AnalyticsAgent:
    """Build the standard agent without requiring database access by default."""

    agent = AnalyticsAgent(config=config)
    agent.register_tool(KpiMetadataTool())
    agent.register_tool(SemanticMetadataTool())
    if include_database:
        agent.register_tool(PostgresAnalyticsTool(config=agent.config))
    return agent
