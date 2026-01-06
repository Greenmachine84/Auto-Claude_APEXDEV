"""Base Module for Agent System.

Provides foundational infrastructure for all agents:
- BaseAgent: Abstract base class for all agents
- AgentConfig: Configuration dataclasses
- AgentState: State management
- ExecutionContext: Execution context
- AgentHooks: APEX lifecycle hooks

All agents inherit from BaseAgent and implement required interfaces.
"""

from .base_agent import BaseAgent
from .agent_config import AgentConfig, AgentCapabilities, ResourceLimits
from .agent_state import AgentStateManager
from .agent_context import ExecutionContext, ContextBuilder
from .agent_hooks import (
    AgentHooks,
    HookType,
    hook,
    pre_execute,
    post_execute,
    on_error,
    on_memory_store,
)

__all__ = [
    # Base Agent
    "BaseAgent",
    # Configuration
    "AgentConfig",
    "AgentCapabilities",
    "ResourceLimits",
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
