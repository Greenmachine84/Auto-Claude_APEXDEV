"""Agent Registry.

Central registry for agent class registration and discovery.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Provides singleton pattern for global agent registry.
"""

import logging
import threading
from typing import Type, Iterator

from ..types import AgentType, AgentCategory, AGENT_CATEGORY_MAP
from ..base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for agent classes.

    Thread-safe singleton registry for registering and discovering
    agent implementations.

    Usage:
        >>> registry = AgentRegistry()
        >>> @registry.register(AgentType.CODER)
        ... class CoderAgent(BaseAgent):
        ...     pass
        ...
        >>> agent_class = registry.get(AgentType.CODER)
    """

    _instance: "AgentRegistry | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "AgentRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize registry state."""
        self._agents: dict[AgentType, Type[BaseAgent]] = {}
        self._metadata: dict[AgentType, dict] = {}
        self._initialized = True

    def register(
        self,
        agent_type: AgentType,
        *,
        override: bool = False,
    ) -> callable:
        """Decorator to register an agent class.

        Args:
            agent_type: Type of agent to register
            override: Allow overriding existing registration

        Returns:
            Decorator function

        Raises:
            ValueError: If agent_type already registered and not override
        """
        def decorator(cls: Type[BaseAgent]) -> Type[BaseAgent]:
            if agent_type in self._agents and not override:
                raise ValueError(
                    f"Agent type {agent_type.value} already registered. "
                    f"Use override=True to replace."
                )

            if not issubclass(cls, BaseAgent):
                raise TypeError(
                    f"Agent class must inherit from BaseAgent, got {cls}"
                )

            self._agents[agent_type] = cls
            self._metadata[agent_type] = {
                "class_name": cls.__name__,
                "module": cls.__module__,
                "description": cls.get_description() if hasattr(cls, 'get_description') else "",
                "category": AGENT_CATEGORY_MAP.get(agent_type, AgentCategory.CORE).value,
            }

            # Set the AGENT_TYPE class variable
            cls.AGENT_TYPE = agent_type

            logger.info(f"Registered agent: {agent_type.value} -> {cls.__name__}")
            return cls

        return decorator

    def register_class(
        self,
        agent_type: AgentType,
        cls: Type[BaseAgent],
        *,
        override: bool = False,
    ) -> None:
        """Programmatically register an agent class.

        Args:
            agent_type: Type of agent
            cls: Agent class to register
            override: Allow overriding existing registration
        """
        self.register(agent_type, override=override)(cls)

    def get(self, agent_type: AgentType) -> Type[BaseAgent] | None:
        """Get an agent class by type.

        Args:
            agent_type: Type of agent to get

        Returns:
            Agent class or None if not found
        """
        return self._agents.get(agent_type)

    def get_or_raise(self, agent_type: AgentType) -> Type[BaseAgent]:
        """Get an agent class, raising if not found.

        Args:
            agent_type: Type of agent to get

        Returns:
            Agent class

        Raises:
            KeyError: If agent not registered
        """
        if agent_type not in self._agents:
            raise KeyError(f"Agent type not registered: {agent_type.value}")
        return self._agents[agent_type]

    def unregister(self, agent_type: AgentType) -> bool:
        """Unregister an agent.

        Args:
            agent_type: Type of agent to unregister

        Returns:
            True if agent was unregistered
        """
        if agent_type in self._agents:
            del self._agents[agent_type]
            del self._metadata[agent_type]
            logger.info(f"Unregistered agent: {agent_type.value}")
            return True
        return False

    def is_registered(self, agent_type: AgentType) -> bool:
        """Check if an agent type is registered.

        Args:
            agent_type: Type to check

        Returns:
            True if registered
        """
        return agent_type in self._agents

    def list_agents(self) -> list[AgentType]:
        """List all registered agent types.

        Returns:
            List of registered agent types
        """
        return list(self._agents.keys())

    def list_by_category(self, category: AgentCategory) -> list[AgentType]:
        """List agents by category.

        Args:
            category: Category to filter by

        Returns:
            List of agent types in category
        """
        return [
            agent_type
            for agent_type in self._agents
            if AGENT_CATEGORY_MAP.get(agent_type) == category
        ]

    def get_metadata(self, agent_type: AgentType) -> dict | None:
        """Get metadata for an agent.

        Args:
            agent_type: Type of agent

        Returns:
            Metadata dict or None
        """
        return self._metadata.get(agent_type)

    def __iter__(self) -> Iterator[tuple[AgentType, Type[BaseAgent]]]:
        """Iterate over registered agents."""
        return iter(self._agents.items())

    def __len__(self) -> int:
        """Get number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_type: AgentType) -> bool:
        """Check if agent type is registered."""
        return agent_type in self._agents

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._agents.clear()
        self._metadata.clear()
        logger.warning("Agent registry cleared")


# Global registry accessor
_global_registry: AgentRegistry | None = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry.

    Returns:
        Singleton AgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry
