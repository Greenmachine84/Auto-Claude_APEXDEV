"""Base Agent Abstract Class.

Defines the abstract base class for all DEVAPEX agents.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

All agents MUST inherit from BaseAgent and implement required methods.
Provides lifecycle management, hook integration, and APEX compliance.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, ClassVar
import uuid

from ..types import AgentType, AgentStatus, AgentResult
from .agent_config import AgentConfig
from .agent_state import AgentStateManager, StateSnapshot
from .agent_context import ExecutionContext
from .agent_hooks import AgentHooks, HookType, HookContext


class BaseAgent(ABC):
    """Abstract base class for all DEVAPEX agents.

    Provides foundational infrastructure for agent lifecycle:
    - State management with validated transitions
    - Configuration and capability management
    - APEX Constitution hooks
    - Logging and observability

    Subclasses must implement:
    - execute(): Core execution logic
    - get_description(): Agent description for registry

    Optional overrides:
    - initialize(): Custom initialization
    - cleanup(): Custom cleanup
    - handle_error(): Custom error handling

    Usage:
        >>> class CoderAgent(BaseAgent):
        ...     def execute(self, context: ExecutionContext) -> AgentResult:
        ...         # Implementation
        ...         pass
        ...
        ...     @classmethod
        ...     def get_description(cls) -> str:
        ...         return "Autonomous code generation agent"
    """

    # Class-level agent type (override in subclasses)
    AGENT_TYPE: ClassVar[AgentType] = AgentType.CODER

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
    ):
        """Initialize the base agent.

        Args:
            config: Agent configuration (uses defaults if None)
            agent_id: Unique agent ID (generated if None)
        """
        self._id = agent_id or f"{self.AGENT_TYPE.value}-{uuid.uuid4().hex[:8]}"
        self._config = config or AgentConfig(agent_type=self.AGENT_TYPE)
        self._state = AgentStateManager(
            initial_status=AgentStatus.IDLE,
            agent_id=self._id,
        )
        self._hooks = AgentHooks(agent_id=self._id)
        self._logger = logging.getLogger(f"agent.{self._id}")
        self._context: ExecutionContext | None = None
        self._initialized = False

        # Register state change callback
        self._state.add_callback(self._on_state_change)

        self._logger.debug(f"BaseAgent initialized: {self._id}")

    @property
    def id(self) -> str:
        """Get agent identifier."""
        return self._id

    @property
    def agent_type(self) -> AgentType:
        """Get agent type."""
        return self.AGENT_TYPE

    @property
    def config(self) -> AgentConfig:
        """Get agent configuration."""
        return self._config

    @property
    def status(self) -> AgentStatus:
        """Get current agent status."""
        return self._state.current_status

    @property
    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._state.is_active

    @property
    def is_healthy(self) -> bool:
        """Check if agent is in a healthy state."""
        return self._state.is_healthy

    @property
    def hooks(self) -> AgentHooks:
        """Get agent hooks."""
        return self._hooks

    @property
    def logger(self) -> logging.Logger:
        """Get agent logger."""
        return self._logger

    @property
    def current_context(self) -> ExecutionContext | None:
        """Get current execution context."""
        return self._context

    # ========================================================================
    # Abstract Methods (must be implemented by subclasses)
    # ========================================================================

    @abstractmethod
    def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute the agent's primary task.

        This is the core method that defines the agent's behavior.
        Must be implemented by all agent subclasses.

        Args:
            context: Execution context with task and permissions

        Returns:
            AgentResult indicating success, failure, or partial completion

        Raises:
            Should not raise exceptions - wrap in ErrorResult
        """
        ...

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Get human-readable agent description.

        Used for agent registry and documentation.

        Returns:
            Description string
        """
        ...

    # ========================================================================
    # Lifecycle Methods (can be overridden)
    # ========================================================================

    def initialize(self) -> None:
        """Initialize the agent.

        Called before first execution. Override for custom initialization.
        Default implementation transitions to INITIALIZING then IDLE.
        """
        if self._initialized:
            self._logger.warning("Agent already initialized")
            return

        self._state.transition_to(
            AgentStatus.INITIALIZING,
            reason="Agent initialization",
        )

        # Hook: initialization
        self._hooks.execute(HookType.ON_STATE_CHANGE)

        self._initialized = True
        self._state.transition_to(
            AgentStatus.IDLE,
            reason="Initialization complete",
        )

    def cleanup(self) -> None:
        """Clean up agent resources.

        Called when agent is being terminated.
        Override for custom cleanup logic.
        """
        self._logger.info(f"Cleaning up agent: {self._id}")

        if self._state.current_status != AgentStatus.TERMINATED:
            self._state.force_transition(
                AgentStatus.TERMINATED,
                reason="Agent cleanup",
            )

        self._context = None
        self._initialized = False

    def handle_error(self, error: Exception, context: ExecutionContext) -> None:
        """Handle execution error.

        Override for custom error handling logic.

        Args:
            error: Exception that occurred
            context: Execution context when error occurred
        """
        self._logger.error(f"Agent error: {error}", exc_info=True)

        self._state.transition_to(
            AgentStatus.ERROR,
            reason=f"Execution error: {type(error).__name__}",
            error_message=str(error),
        )

        self._hooks.execute(
            HookType.ON_ERROR,
            error=error,
            metadata={"context_id": context.context_id},
        )

    # ========================================================================
    # Execution Flow
    # ========================================================================

    def run(self, context: ExecutionContext) -> AgentResult:
        """Run the agent with full lifecycle management.

        This is the main entry point for agent execution.
        Handles state transitions, hooks, and error handling.

        Args:
            context: Execution context

        Returns:
            AgentResult from execution
        """
        if not self._initialized:
            self.initialize()

        self._context = context

        # Pre-execution hook
        self._hooks.execute(
            HookType.PRE_EXECUTE,
            metadata={"context_id": context.context_id},
        )

        # Transition to running
        self._state.transition_to(
            AgentStatus.RUNNING,
            reason=f"Starting task: {context.task.description if context.task else 'unnamed'}",
        )

        try:
            # Execute core logic
            result = self.execute(context)

            # Post-execution hook
            self._hooks.execute(
                HookType.POST_EXECUTE,
                result=result,
                metadata={"context_id": context.context_id},
            )

            # Transition back to idle
            self._state.transition_to(
                AgentStatus.IDLE,
                reason="Execution complete",
            )

            return result

        except Exception as e:
            self.handle_error(e, context)
            from ..types import ErrorResult, ErrorCode
            return ErrorResult(
                message=str(e),
                code=ErrorCode.EXECUTION_ERROR,
                recoverable=False,
            )
        finally:
            self._context = None

    def pause(self) -> bool:
        """Pause agent execution.

        Returns:
            True if pause was successful
        """
        try:
            self._state.transition_to(
                AgentStatus.PAUSED,
                reason="Agent paused",
            )
            return True
        except Exception:
            return False

    def resume(self) -> bool:
        """Resume agent execution.

        Returns:
            True if resume was successful
        """
        try:
            self._state.transition_to(
                AgentStatus.RUNNING,
                reason="Agent resumed",
            )
            return True
        except Exception:
            return False

    def terminate(self) -> None:
        """Terminate the agent."""
        self._state.force_transition(
            AgentStatus.TERMINATED,
            reason="Agent terminated",
        )
        self.cleanup()

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _on_state_change(self, snapshot: StateSnapshot) -> None:
        """Handle state change events.

        Args:
            snapshot: State snapshot with change info
        """
        self._hooks.execute(
            HookType.ON_STATE_CHANGE,
            metadata={
                "status": snapshot.status.value,
                "previous": snapshot.previous_status.value if snapshot.previous_status else None,
                "reason": snapshot.transition_reason,
            },
        )

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_state_history(self) -> list[StateSnapshot]:
        """Get agent state history."""
        return self._state.history

    def to_dict(self) -> dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "id": self._id,
            "type": self.agent_type.value,
            "status": self.status.value,
            "is_healthy": self.is_healthy,
            "initialized": self._initialized,
            "config": {
                "name": self._config.name,
                "priority": self._config.priority.name,
                "enable_memory": self._config.enable_memory,
                "enable_tools": self._config.enable_tools,
            },
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, status={self.status.value!r})"
