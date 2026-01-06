"""Base Enterprise Agent.

Provides common functionality for all enterprise agents.
Extends BaseAgent with enterprise-specific capabilities.
"""

from abc import abstractmethod
from typing import ClassVar, Any

from ..types import AgentType, AgentResult
from ..base import BaseAgent, AgentConfig, ExecutionContext


class BaseEnterpriseAgent(BaseAgent):
    """Base class for enterprise agents.

    Extends BaseAgent with:
    - Enterprise-specific configuration
    - Extended logging and metrics
    - Compliance integration
    """

    # Enterprise agents should override this
    AGENT_CATEGORY: ClassVar[str] = "enterprise"

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
    ):
        super().__init__(config=config, agent_id=agent_id)
        self._metrics: dict[str, Any] = {}

    def record_metric(self, name: str, value: Any) -> None:
        """Record a metric."""
        self._metrics[name] = value

    def get_metrics(self) -> dict[str, Any]:
        """Get recorded metrics."""
        return dict(self._metrics)
