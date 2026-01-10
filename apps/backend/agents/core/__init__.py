"""Core Agents Module.

Implements the 4 core agents defined in PHASE1_AGENT_SYSTEM_ARCHITECTURE.md:
- CoderAgent: Autonomous code generation
- ReviewerAgent: Code review and validation
- FixerAgent: Issue resolution
- OrchestratorAgent: Multi-agent coordination

All core agents inherit from BaseAgent and are registered with the registry.
"""

from .coder_agent import CoderAgent
from .fixer_agent import FixerAgent
from .orchestrator_agent import OrchestratorAgent
from .reviewer_agent import ReviewerAgent

__all__ = [
    "CoderAgent",
    "ReviewerAgent",
    "FixerAgent",
    "OrchestratorAgent",
]

# Register all core agents on import
from ..registry import get_registry
from ..types import AgentType

_registry = get_registry()
_registry.register_class(AgentType.CODER, CoderAgent, override=True)
_registry.register_class(AgentType.REVIEWER, ReviewerAgent, override=True)
_registry.register_class(AgentType.FIXER, FixerAgent, override=True)
_registry.register_class(AgentType.ORCHESTRATOR, OrchestratorAgent, override=True)
