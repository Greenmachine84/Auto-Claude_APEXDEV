"""Agent Factory.

Factory pattern for creating agent instances.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Provides centralized agent instantiation with configuration.
"""

import logging
from typing import Any

from ..base import AgentConfig, BaseAgent
from ..types import AgentType
from .agent_registry import get_registry

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating agent instances.

    Creates configured agent instances from the registry.
    Supports custom configuration and dependency injection.

    Usage:
        >>> factory = AgentFactory()
        >>> coder = factory.create(AgentType.CODER, name="my-coder")
    """

    def __init__(self, registry=None):
        """Initialize factory.

        Args:
            registry: Optional registry to use (defaults to global)
        """
        self._registry = registry or get_registry()

    def create(
        self,
        agent_type: AgentType,
        *,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
        **config_kwargs: Any,
    ) -> BaseAgent:
        """Create an agent instance.

        Args:
            agent_type: Type of agent to create
            config: Optional pre-built configuration
            agent_id: Optional agent ID
            **config_kwargs: Additional config parameters

        Returns:
            Configured agent instance

        Raises:
            KeyError: If agent type not registered
        """
        agent_class = self._registry.get_or_raise(agent_type)

        # Build config if not provided
        if config is None:
            config = AgentConfig(agent_type=agent_type, **config_kwargs)

        # Create instance
        agent = agent_class(config=config, agent_id=agent_id)

        logger.debug(f"Created agent: {agent.id} (type={agent_type.value})")

        return agent

    def create_coder(self, **kwargs: Any) -> BaseAgent:
        """Create a coder agent.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Coder agent instance
        """
        return self.create(
            AgentType.CODER,
            config=AgentConfig.for_coder(**kwargs),
        )

    def create_reviewer(self, **kwargs: Any) -> BaseAgent:
        """Create a reviewer agent.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Reviewer agent instance
        """
        return self.create(
            AgentType.REVIEWER,
            config=AgentConfig.for_reviewer(**kwargs),
        )

    def create_orchestrator(self, **kwargs: Any) -> BaseAgent:
        """Create an orchestrator agent.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Orchestrator agent instance
        """
        return self.create(
            AgentType.ORCHESTRATOR,
            config=AgentConfig.for_orchestrator(**kwargs),
        )

    def can_create(self, agent_type: AgentType) -> bool:
        """Check if an agent type can be created.

        Args:
            agent_type: Type to check

        Returns:
            True if agent type is registered
        """
        return self._registry.is_registered(agent_type)

    def list_available(self) -> list[AgentType]:
        """List available agent types.

        Returns:
            List of registered agent types
        """
        return self._registry.list_agents()


# Convenience function
def create_agent(
    agent_type: AgentType,
    **kwargs: Any,
) -> BaseAgent:
    """Create an agent instance using the default factory.

    Args:
        agent_type: Type of agent to create
        **kwargs: Configuration parameters

    Returns:
        Agent instance
    """
    return AgentFactory().create(agent_type, **kwargs)
