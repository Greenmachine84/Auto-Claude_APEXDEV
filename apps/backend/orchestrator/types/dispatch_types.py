"""Dispatch type definitions.

Defines types for task dispatch.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DispatchPolicy(str, Enum):
    """Dispatch policy values."""

    IMMEDIATE = "immediate"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    BATCHED = "batched"
    PRIORITY = "priority"


class DispatchMode(str, Enum):
    """Dispatch mode values."""

    SYNC = "sync"
    ASYNC = "async"
    FIRE_AND_FORGET = "fire_and_forget"
    CALLBACK = "callback"


@dataclass
class DispatchEvent:
    """An event in dispatch lifecycle."""

    event_type: str
    task_id: str
    agent_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    # Event data
    status: str | None = None
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "message": self.message,
            "data": self.data,
        }


@dataclass
class DispatchConfig:
    """Configuration for dispatch."""

    # Policy
    policy: DispatchPolicy = DispatchPolicy.QUEUED
    mode: DispatchMode = DispatchMode.ASYNC

    # Timing
    timeout: float = 300.0
    delay: float = 0.0

    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # Load balancing
    load_balancing: str = "least_connections"
    sticky_agent: bool = False

    # Batching
    batch_size: int = 10
    batch_timeout: float = 5.0

    # Callback
    callback_url: str | None = None
    callback_headers: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy": self.policy.value,
            "mode": self.mode.value,
            "timeout": self.timeout,
            "delay": self.delay,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "retry_backoff": self.retry_backoff,
            "load_balancing": self.load_balancing,
            "sticky_agent": self.sticky_agent,
            "batch_size": self.batch_size,
            "batch_timeout": self.batch_timeout,
            "callback_url": self.callback_url,
            "callback_headers": self.callback_headers,
        }
