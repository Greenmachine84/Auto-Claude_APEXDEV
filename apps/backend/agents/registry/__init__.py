"""Agent Registry Module.

Provides agent registration, discovery, and factory patterns.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

The registry is the central point for:
- Registering agent classes
- Creating agent instances
- Discovering available agents
- Managing agent metadata
"""

from .agent_catalog import AgentCatalog, AgentMetadata
from .agent_factory import AgentFactory, create_agent
from .agent_registry import AgentRegistry, get_registry

__all__ = [
    # Factory
    "AgentFactory",
    "create_agent",
    # Registry
    "AgentRegistry",
    "get_registry",
    # Catalog
    "AgentCatalog",
    "AgentMetadata",
]
