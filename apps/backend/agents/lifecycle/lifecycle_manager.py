"""Agent Lifecycle Manager.

Manages agent lifecycle events and transitions.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Provides:
- Lifecycle event tracking
- Transition management
- Event callbacks
"""

import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from ..types import AgentStatus
from ..base import BaseAgent

logger = logging.getLogger(__name__)


class LifecycleEvent(Enum):
    """Agent lifecycle events."""

    CREATED = auto()
    INITIALIZED = auto()
    STARTED = auto()
    PAUSED = auto()
    RESUMED = auto()
    COMPLETED = auto()
    FAILED = auto()
    TERMINATED = auto()
    RESTARTED = auto()


@dataclass
class LifecycleRecord:
    """Record of a lifecycle event."""

    event: LifecycleEvent
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    previous_status: AgentStatus | None = None
    new_status: AgentStatus | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event": self.event.name,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "previous_status": self.previous_status.value if self.previous_status else None,
            "new_status": self.new_status.value if self.new_status else None,
            "metadata": self.metadata,
        }


LifecycleCallback = Callable[[LifecycleRecord], None]


class LifecycleManager:
    """Manages agent lifecycle events.

    Tracks lifecycle events and provides callbacks for monitoring.
    Integrates with APEX Constitution governance.

    Usage:
        >>> manager = LifecycleManager()
        >>> manager.on_event(LifecycleEvent.STARTED, my_callback)
        >>> manager.track(agent)
        >>> agent.run(context)
    """

    def __init__(self, max_history: int = 1000):
        """Initialize lifecycle manager.

        Args:
            max_history: Maximum events to keep in history
        """
        self._callbacks: dict[LifecycleEvent, list[LifecycleCallback]] = {
            event: [] for event in LifecycleEvent
        }
        self._global_callbacks: list[LifecycleCallback] = []
        self._history: list[LifecycleRecord] = []
        self._max_history = max_history
        self._tracked_agents: dict[str, BaseAgent] = {}

    def on_event(
        self,
        event: LifecycleEvent | None = None,
    ) -> Callable[[LifecycleCallback], LifecycleCallback]:
        """Decorator to register event callback.

        Args:
            event: Specific event to listen for, or None for all

        Returns:
            Decorator function
        """
        def decorator(func: LifecycleCallback) -> LifecycleCallback:
            if event is None:
                self._global_callbacks.append(func)
            else:
                self._callbacks[event].append(func)
            return func
        return decorator

    def add_callback(
        self,
        callback: LifecycleCallback,
        event: LifecycleEvent | None = None,
    ) -> None:
        """Add an event callback.

        Args:
            callback: Callback function
            event: Specific event, or None for all
        """
        if event is None:
            self._global_callbacks.append(callback)
        else:
            self._callbacks[event].append(callback)

    def track(self, agent: BaseAgent) -> None:
        """Start tracking an agent's lifecycle.

        Args:
            agent: Agent to track
        """
        self._tracked_agents[agent.id] = agent
        self._emit(LifecycleEvent.CREATED, agent)

    def untrack(self, agent: BaseAgent) -> None:
        """Stop tracking an agent.

        Args:
            agent: Agent to untrack
        """
        if agent.id in self._tracked_agents:
            del self._tracked_agents[agent.id]

    def emit(
        self,
        event: LifecycleEvent,
        agent: BaseAgent,
        previous_status: AgentStatus | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit a lifecycle event.

        Args:
            event: Event type
            agent: Agent the event is for
            previous_status: Previous agent status
            metadata: Additional event data
        """
        self._emit(event, agent, previous_status, metadata)

    def _emit(
        self,
        event: LifecycleEvent,
        agent: BaseAgent,
        previous_status: AgentStatus | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Internal emit implementation."""
        record = LifecycleRecord(
            event=event,
            agent_id=agent.id,
            previous_status=previous_status,
            new_status=agent.status,
            metadata=metadata or {},
        )

        # Add to history
        self._history.append(record)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Execute callbacks
        for callback in self._callbacks[event]:
            try:
                callback(record)
            except Exception as e:
                logger.error(f"Lifecycle callback error: {e}")

        for callback in self._global_callbacks:
            try:
                callback(record)
            except Exception as e:
                logger.error(f"Global lifecycle callback error: {e}")

    def get_history(
        self,
        agent_id: str | None = None,
        event: LifecycleEvent | None = None,
        limit: int | None = None,
    ) -> list[LifecycleRecord]:
        """Get lifecycle history.

        Args:
            agent_id: Filter by agent ID
            event: Filter by event type
            limit: Maximum records to return

        Returns:
            List of lifecycle records
        """
        records = self._history

        if agent_id:
            records = [r for r in records if r.agent_id == agent_id]

        if event:
            records = [r for r in records if r.event == event]

        if limit:
            records = records[-limit:]

        return records

    def get_tracked_agents(self) -> list[BaseAgent]:
        """Get all tracked agents.

        Returns:
            List of tracked agents
        """
        return list(self._tracked_agents.values())

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()
