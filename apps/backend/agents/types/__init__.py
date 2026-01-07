"""Agent Types Module.

Provides type definitions for the agent system including:
- AgentType: Enumeration of all agent types (4 core + 15 enterprise)
- Priority: Task priority levels
- AgentStatus: Agent lifecycle states
- AgentResult: Standardized result types

This module is the foundation for type safety across the agent system.
All types are immutable and follow APEX Constitution governance.
"""

from .agent_types import AgentType, AgentCategory, AGENT_CATEGORY_MAP
from .priority_types import Priority
from .status_types import AgentStatus, InvalidStatusTransitionError
from .result_types import (
    AgentResult,
    SuccessResult,
    ErrorResult,
    PartialResult,
    ResultStatus,
    ErrorCode,
)

__all__ = [
    # Agent Types
    "AgentType",
    "AgentCategory",
    "AGENT_CATEGORY_MAP",
    # Priority
    "Priority",
    # Status
    "AgentStatus",
    "InvalidStatusTransitionError",
    # Results
    "AgentResult",
    "SuccessResult",
    "ErrorResult",
    "PartialResult",
    "ResultStatus",
    "ErrorCode",
]