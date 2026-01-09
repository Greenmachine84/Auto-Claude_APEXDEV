"""Workflow type definitions.

Defines types for workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WorkflowType(str, Enum):
    """Workflow type classification."""

    # Development workflows
    BUILD_AND_TEST = "build_and_test"
    CODE_REVIEW = "code_review"
    DEPLOYMENT = "deployment"

    # CI/CD workflows
    CONTINUOUS_INTEGRATION = "ci"
    CONTINUOUS_DEPLOYMENT = "cd"

    # Data workflows
    DATA_PIPELINE = "data_pipeline"
    ETL = "etl"

    # Custom
    CUSTOM = "custom"


class WorkflowPhase(str, Enum):
    """Workflow phase values."""

    INITIALIZATION = "initialization"
    SETUP = "setup"
    EXECUTION = "execution"
    VALIDATION = "validation"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowEvent:
    """An event in workflow execution."""

    event_type: str
    workflow_id: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Event data
    step_id: str | None = None
    phase: WorkflowPhase | None = None
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "workflow_id": self.workflow_id,
            "timestamp": self.timestamp.isoformat(),
            "step_id": self.step_id,
            "phase": self.phase.value if self.phase else None,
            "message": self.message,
            "data": self.data,
        }


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    # Execution
    timeout: float = 3600.0
    max_parallel_steps: int = 4

    # Error handling
    fail_fast: bool = True
    continue_on_step_failure: bool = False
    max_step_retries: int = 2

    # Notifications
    notify_on_start: bool = False
    notify_on_complete: bool = True
    notify_on_failure: bool = True
    notification_channels: list[str] = field(default_factory=list)

    # Persistence
    persist_state: bool = True
    checkpoint_interval: int = 0  # 0 = disabled

    # Custom settings
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeout": self.timeout,
            "max_parallel_steps": self.max_parallel_steps,
            "fail_fast": self.fail_fast,
            "continue_on_step_failure": self.continue_on_step_failure,
            "max_step_retries": self.max_step_retries,
            "notify_on_start": self.notify_on_start,
            "notify_on_complete": self.notify_on_complete,
            "notify_on_failure": self.notify_on_failure,
            "notification_channels": self.notification_channels,
            "persist_state": self.persist_state,
            "checkpoint_interval": self.checkpoint_interval,
            "custom": self.custom,
        }
