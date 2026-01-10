"""Result type definitions.

Defines types for tool execution results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    """Result status classification."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class ResultType(str, Enum):
    """Result type classification."""

    TEXT = "text"
    JSON = "json"
    BINARY = "binary"
    STREAM = "stream"
    FILE = "file"
    ERROR = "error"


@dataclass
class ResultMetrics:
    """Metrics about result execution."""

    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float = 0.0
    memory_bytes: int = 0
    cpu_percent: float = 0.0
    tokens_used: int = 0
    api_calls: int = 0
    retries: int = 0

    def calculate_duration(self) -> None:
        """Calculate duration from timestamps."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_ms = delta.total_seconds() * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "memory_bytes": self.memory_bytes,
            "cpu_percent": self.cpu_percent,
            "tokens_used": self.tokens_used,
            "api_calls": self.api_calls,
            "retries": self.retries,
        }


@dataclass
class ResultArtifact:
    """An artifact produced by tool execution."""

    name: str
    type: ResultType
    content: Any
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ToolResult:
    """Complete tool execution result."""

    tool_name: str
    status: ResultStatus
    output: Any
    error: str | None = None
    metrics: ResultMetrics | None = None
    artifacts: list[ResultArtifact] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if result is successful."""
        return self.status == ResultStatus.COMPLETED

    @property
    def failed(self) -> bool:
        """Check if result failed."""
        return self.status in (ResultStatus.FAILED, ResultStatus.TIMEOUT)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metadata": self.metadata,
        }

    @classmethod
    def success_result(
        cls,
        tool_name: str,
        output: Any,
        metrics: ResultMetrics | None = None,
    ) -> "ToolResult":
        """Create a success result."""
        return cls(
            tool_name=tool_name,
            status=ResultStatus.COMPLETED,
            output=output,
            metrics=metrics,
        )

    @classmethod
    def error_result(
        cls,
        tool_name: str,
        error: str,
        metrics: ResultMetrics | None = None,
    ) -> "ToolResult":
        """Create an error result."""
        return cls(
            tool_name=tool_name,
            status=ResultStatus.FAILED,
            output=None,
            error=error,
            metrics=metrics,
        )


@dataclass
class BatchResult:
    """Result of batch tool execution."""

    results: list[ToolResult]
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    metrics: ResultMetrics | None = None

    def __post_init__(self) -> None:
        """Calculate counts."""
        self.total_count = len(self.results)
        self.success_count = sum(1 for r in self.results if r.success)
        self.failure_count = sum(1 for r in self.results if r.failed)

    @property
    def all_success(self) -> bool:
        """Check if all results succeeded."""
        return self.failure_count == 0

    @property
    def partial_success(self) -> bool:
        """Check if some results succeeded."""
        return 0 < self.success_count < self.total_count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }
