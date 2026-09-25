"""Retail360 agentic analytics package.

The package keeps AI orchestration separate from the governed warehouse,
semantic model, and validation layers.
"""

from .config import AgentConfig
from .orchestrator import AnalyticsAgent, AgentResponse

__all__ = ["AgentConfig", "AnalyticsAgent", "AgentResponse"]
