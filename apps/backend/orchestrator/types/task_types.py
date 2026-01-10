"""Task type definitions.

Defines types for tasks.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    """Task type classification."""

    # Code tasks
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_REFACTOR = "code_refactor"

    # Test tasks
    TEST_GENERATION = "test_generation"
    TEST_EXECUTION = "test_execution"

    # Analysis tasks
    STATIC_ANALYSIS = "static_analysis"
    SECURITY_SCAN = "security_scan"
    DEPENDENCY_CHECK = "dependency_check"

    # Documentation tasks
    DOC_GENERATION = "doc_generation"
    DOC_UPDATE = "doc_update"

    # Build tasks
    BUILD = "build"
    DEPLOY = "deploy"

    # Utility tasks
    SHELL_COMMAND = "shell_command"
    FILE_OPERATION = "file_operation"
    API_CALL = "api_call"


class TaskState(str, Enum):
    """Task state values."""

    CREATED = "created"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    ASSIGNED = "assigned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class TaskMetadata:
    """Metadata for a task."""

    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, Any] = field(default_factory=dict)

    # Tracking
    source: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "labels": self.labels,
            "annotations": self.annotations,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
        }


@dataclass
class TaskConfig:
    """Configuration for task execution."""

    # Execution
    timeout: float = 300.0
    retries: int = 3
    retry_delay: float = 1.0

    # Resources
    memory_limit_mb: int = 512
    cpu_limit: float = 1.0

    # Capabilities
    required_capabilities: set[str] = field(default_factory=set)
    preferred_agent: str | None = None

    # Behavior
    continue_on_error: bool = False
    capture_output: bool = True
    stream_output: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeout": self.timeout,
            "retries": self.retries,
            "retry_delay": self.retry_delay,
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_limit": self.cpu_limit,
            "required_capabilities": list(self.required_capabilities),
            "preferred_agent": self.preferred_agent,
            "continue_on_error": self.continue_on_error,
            "capture_output": self.capture_output,
            "stream_output": self.stream_output,
        }
