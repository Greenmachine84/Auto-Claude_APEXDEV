"""Base Module for Agent System.

Provides foundational infrastructure for all agents:
- BaseAgent: Abstract base class for all agents
- AgentConfig: Configuration dataclasses
- AgentState: State management
- ExecutionContext: Execution context
- AgentHooks: APEX lifecycle hooks

All agents inherit from BaseAgent and implement required interfaces.
"""

# Configuration constants (from parent base.py)
AUTO_CONTINUE_DELAY_SECONDS = 3
HUMAN_INTERVENTION_FILE = "PAUSE"

from .agent_config import (
    CODER_CAPABILITIES,
    ORCHESTRATOR_CAPABILITIES,
    READ_ONLY_CAPABILITIES,
    REVIEWER_CAPABILITIES,
    AgentCapabilities,
    AgentConfig,
    ResourceLimits,
)
from .agent_context import ContextBuilder, ExecutionContext
from .agent_hooks import (
    AgentHooks,
    HookType,
    hook,
    on_error,
    on_memory_store,
    post_execute,
    pre_execute,
)
from .agent_state import AgentStateManager
from .base_agent import BaseAgent

__all__ = [
    # Base Agent
    "BaseAgent",
    # Configuration
    "AgentConfig",
    "AgentCapabilities",
    "ResourceLimits",
    # Capability Constants
    "READ_ONLY_CAPABILITIES",
    "CODER_CAPABILITIES",
    "REVIEWER_CAPABILITIES",
    "ORCHESTRATOR_CAPABILITIES",
    # State
    "AgentStateManager",
    # Context
    "ExecutionContext",
    "ContextBuilder",
    # Hooks
    "AgentHooks",
    "HookType",
    "hook",
    "pre_execute",
    "post_execute",
    "on_error",
    "on_memory_store",
]
