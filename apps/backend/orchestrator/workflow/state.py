"""Workflow state.

Tracks workflow execution state.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WorkflowStatus(str, Enum):
    """Workflow status values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class StepState:
    """State of a workflow step."""

    step_id: str
    step_name: str
    status: str = "pending"

    # Timestamps
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Results
    outputs: Any = None
    error: str | None = None

    # Execution
    retries: int = 0

    @property
    def is_complete(self) -> bool:
        """Check if step is complete."""
        return self.status in ("completed", "failed", "skipped")

    @property
    def is_success(self) -> bool:
        """Check if step succeeded."""
        return self.status == "completed"

    @property
    def duration(self) -> float | None:
        """Get step duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "outputs": self.outputs,
            "error": self.error,
            "duration": self.duration,
            "retries": self.retries,
        }


@dataclass
class WorkflowState:
    """State of a workflow execution."""

    workflow_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Input/output
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)

    # Step states
    step_states: dict[str, StepState] = field(default_factory=dict)

    # Error
    error: str | None = None

    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.status in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        )

    @property
    def is_success(self) -> bool:
        """Check if workflow succeeded."""
        return self.status == WorkflowStatus.COMPLETED

    @property
    def has_failures(self) -> bool:
        """Check if any step failed."""
        return any(s.status == "failed" for s in self.step_states.values())

    @property
    def duration(self) -> float | None:
        """Get workflow duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def completed_steps(self) -> int:
        """Get count of completed steps."""
        return sum(1 for s in self.step_states.values() if s.is_complete)

    @property
    def total_steps(self) -> int:
        """Get total step count."""
        return len(self.step_states)

    def add_step_state(self, state: StepState) -> None:
        """Add step state."""
        self.step_states[state.step_id] = state

    def get_step_state(self, step_id: str) -> StepState | None:
        """Get step state."""
        return self.step_states.get(step_id)

    def set_output(self, key: str, value: Any) -> None:
        """Set workflow output."""
        self.outputs[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "step_states": {k: v.to_dict() for k, v in self.step_states.items()},
            "error": self.error,
            "duration": self.duration,
            "progress": f"{self.completed_steps}/{self.total_steps}",
        }
