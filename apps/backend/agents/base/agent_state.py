"""Agent State Management.

Manages agent lifecycle state with thread-safe transitions.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

State transitions are validated against APEX governance rules.
"""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..types import AgentStatus, InvalidStatusTransitionError

logger = logging.getLogger(__name__)


@dataclass
class StateSnapshot:
    """Immutable snapshot of agent state at a point in time."""

    status: AgentStatus
    timestamp: datetime
    previous_status: AgentStatus | None = None
    transition_reason: str = ""
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "previous_status": self.previous_status.value
            if self.previous_status
            else None,
            "transition_reason": self.transition_reason,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


StateChangeCallback = Callable[[StateSnapshot], None]


class AgentStateManager:
    """Thread-safe state management for agents.

    Manages agent lifecycle state with validated transitions.
    Supports state change callbacks for event-driven updates.

    Usage:
        >>> state_manager = AgentStateManager()
        >>> state_manager.transition_to(AgentStatus.INITIALIZING)
        >>> state_manager.current_status
        AgentStatus.INITIALIZING
    """

    def __init__(
        self,
        initial_status: AgentStatus = AgentStatus.IDLE,
        agent_id: str | None = None,
    ):
        """Initialize state manager.

        Args:
            initial_status: Starting status (default: IDLE)
            agent_id: Optional agent identifier for logging
        """
        self._status = initial_status
        self._agent_id = agent_id or "unknown"
        self._lock = threading.RLock()
        self._callbacks: list[StateChangeCallback] = []
        self._history: list[StateSnapshot] = []
        self._error_message: str | None = None
        self._metadata: dict[str, Any] = {}

        # Record initial state
        self._record_state(initial_status, None, "Initial state")

    @property
    def current_status(self) -> AgentStatus:
        """Get current agent status."""
        with self._lock:
            return self._status

    @property
    def is_active(self) -> bool:
        """Check if agent is in an active state."""
        return self.current_status.is_active()

    @property
    def is_healthy(self) -> bool:
        """Check if agent is in a healthy state."""
        return self.current_status.is_healthy()

    @property
    def error_message(self) -> str | None:
        """Get the current error message if in ERROR state."""
        with self._lock:
            return self._error_message

    @property
    def history(self) -> list[StateSnapshot]:
        """Get state transition history."""
        with self._lock:
            return list(self._history)

    def transition_to(
        self,
        target: AgentStatus,
        reason: str = "",
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Transition to a new status.

        Args:
            target: Target status to transition to
            reason: Human-readable reason for transition
            error_message: Error message if transitioning to ERROR
            metadata: Additional metadata for the transition

        Returns:
            True if transition was successful

        Raises:
            InvalidStatusTransitionError: If transition is not valid
        """
        with self._lock:
            current = self._status

            if not current.can_transition_to(target):
                raise InvalidStatusTransitionError(current, target)

            # Update state
            self._status = target
            self._error_message = error_message if target == AgentStatus.ERROR else None
            if metadata:
                self._metadata.update(metadata)

            # Record state change
            snapshot = self._record_state(target, current, reason, error_message)

            logger.info(
                f"Agent {self._agent_id}: {current.value} -> {target.value}"
                + (f" ({reason})" if reason else "")
            )

        # Notify callbacks outside of lock
        self._notify_callbacks(snapshot)
        return True

    def force_transition(
        self,
        target: AgentStatus,
        reason: str = "Forced transition",
    ) -> None:
        """Force transition to a status without validation.

        Use sparingly - only for recovery scenarios.

        Args:
            target: Target status
            reason: Reason for forced transition
        """
        with self._lock:
            current = self._status
            self._status = target

            snapshot = self._record_state(target, current, f"[FORCED] {reason}")

            logger.warning(
                f"Agent {self._agent_id}: FORCED {current.value} -> {target.value} ({reason})"
            )

        self._notify_callbacks(snapshot)

    def add_callback(self, callback: StateChangeCallback) -> None:
        """Register a state change callback.

        Args:
            callback: Function to call on state changes
        """
        with self._lock:
            self._callbacks.append(callback)

    def remove_callback(self, callback: StateChangeCallback) -> None:
        """Remove a state change callback.

        Args:
            callback: Callback to remove
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def get_snapshot(self) -> StateSnapshot:
        """Get current state snapshot."""
        with self._lock:
            return StateSnapshot(
                status=self._status,
                timestamp=datetime.now(timezone.utc),
                previous_status=self._history[-1].previous_status
                if self._history
                else None,
                error_message=self._error_message,
                metadata=dict(self._metadata),
            )

    def _record_state(
        self,
        status: AgentStatus,
        previous: AgentStatus | None,
        reason: str,
        error_message: str | None = None,
    ) -> StateSnapshot:
        """Record state transition in history."""
        snapshot = StateSnapshot(
            status=status,
            timestamp=datetime.now(timezone.utc),
            previous_status=previous,
            transition_reason=reason,
            error_message=error_message,
            metadata=dict(self._metadata),
        )
        self._history.append(snapshot)

        # Keep history bounded
        if len(self._history) > 100:
            self._history = self._history[-100:]

        return snapshot

    def _notify_callbacks(self, snapshot: StateSnapshot) -> None:
        """Notify all registered callbacks of state change."""
        for callback in self._callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                logger.error(f"State callback error: {e}")
