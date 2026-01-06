"""Agent Lifecycle Module.

Provides lifecycle management infrastructure for agents.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

The lifecycle module manages:
- Agent pool management
- Lifecycle state transitions
- Supervised execution
- Resource cleanup
"""

from .agent_pool import AgentPool, PoolConfig
from .lifecycle_manager import LifecycleManager, LifecycleEvent
from .supervisor import AgentSupervisor, SupervisorConfig

__all__ = [
    # Pool
    "AgentPool",
    "PoolConfig",
    # Lifecycle
    "LifecycleManager",
    "LifecycleEvent",
    # Supervisor
    "AgentSupervisor",
    "SupervisorConfig",
]
