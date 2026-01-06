"""Agent Catalog.

Provides metadata and documentation for available agents.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

The catalog provides:
- Agent metadata and descriptions
- Capability documentation
- Usage examples
- Category organization
"""

from dataclasses import dataclass, field
from typing import Any

from ..types import AgentType, AgentCategory, AGENT_CATEGORY_MAP
from .agent_registry import get_registry


@dataclass
class AgentMetadata:
    """Metadata for a registered agent."""

    agent_type: AgentType
    name: str
    description: str
    category: AgentCategory
    class_name: str
    module: str
    capabilities: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "class_name": self.class_name,
            "module": self.module,
            "capabilities": self.capabilities,
            "examples": self.examples,
            "tags": self.tags,
            "version": self.version,
        }


class AgentCatalog:
    """Catalog of available agents with rich metadata.

    Provides a queryable view of all registered agents
    with their metadata, capabilities, and documentation.

    Usage:
        >>> catalog = AgentCatalog()
        >>> for agent in catalog.list_all():
        ...     print(f"{agent.name}: {agent.description}")
    """

    def __init__(self, registry=None):
        """Initialize catalog.

        Args:
            registry: Optional registry to use (defaults to global)
        """
        self._registry = registry or get_registry()

    def get(self, agent_type: AgentType) -> AgentMetadata | None:
        """Get metadata for an agent.

        Args:
            agent_type: Type of agent

        Returns:
            AgentMetadata or None if not found
        """
        if not self._registry.is_registered(agent_type):
            return None

        raw = self._registry.get_metadata(agent_type)
        if not raw:
            return None

        return AgentMetadata(
            agent_type=agent_type,
            name=raw.get("class_name", agent_type.value),
            description=raw.get("description", ""),
            category=AGENT_CATEGORY_MAP.get(agent_type, AgentCategory.CORE),
            class_name=raw.get("class_name", ""),
            module=raw.get("module", ""),
        )

    def list_all(self) -> list[AgentMetadata]:
        """List all registered agents.

        Returns:
            List of AgentMetadata for all agents
        """
        return [
            metadata
            for agent_type in self._registry.list_agents()
            if (metadata := self.get(agent_type)) is not None
        ]

    def list_by_category(self, category: AgentCategory) -> list[AgentMetadata]:
        """List agents by category.

        Args:
            category: Category to filter by

        Returns:
            List of AgentMetadata in category
        """
        return [
            metadata
            for agent_type in self._registry.list_by_category(category)
            if (metadata := self.get(agent_type)) is not None
        ]

    def search(self, query: str) -> list[AgentMetadata]:
        """Search agents by name or description.

        Args:
            query: Search query (case-insensitive)

        Returns:
            Matching AgentMetadata entries
        """
        query_lower = query.lower()
        return [
            metadata
            for metadata in self.list_all()
            if query_lower in metadata.name.lower()
            or query_lower in metadata.description.lower()
        ]

    def get_categories(self) -> list[AgentCategory]:
        """Get all categories with registered agents.

        Returns:
            List of categories
        """
        return list(set(
            AGENT_CATEGORY_MAP.get(agent_type, AgentCategory.CORE)
            for agent_type in self._registry.list_agents()
        ))

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Export catalog as dictionary organized by category.

        Returns:
            Dict with categories as keys and agent lists as values
        """
        result: dict[str, list[dict[str, Any]]] = {}
        for category in AgentCategory:
            agents = self.list_by_category(category)
            if agents:
                result[category.value] = [a.to_dict() for a in agents]
        return result
