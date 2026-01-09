"""Agent Result Type Definitions.

Defines standardized result types for agent operations.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Result types provide:
- Type-safe operation outcomes
- Consistent error handling
- Serialization support
- APEX compliance metadata
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final, Generic, TypeVar

T = TypeVar("T")  # Generic type for result data


class ResultStatus(Enum):
    """Status of an agent operation result."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class ResultMetadata:
    """Metadata for agent operation results.

    Provides audit trail and debugging information.
    Immutable for APEX compliance.
    """

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agent_id: str | None = None
    task_id: str | None = None
    session_id: str | None = None
    duration_ms: float | None = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "result_id": self.result_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
        }


@dataclass
class AgentResult(ABC, Generic[T]):
    """Abstract base class for agent operation results.

    All agent operations return an AgentResult subclass.
    Provides consistent interface for success, error, and partial results.

    Type Parameters:
        T: The type of data contained in the result

    Usage:
        >>> result = SuccessResult(data={"files_modified": 3})
        >>> result.is_success()
        True
        >>> result.unwrap()
        {'files_modified': 3}
    """

    status: ResultStatus
    message: str = ""
    metadata: ResultMetadata = field(default_factory=ResultMetadata)

    @abstractmethod
    def is_success(self) -> bool:
        """Check if the operation was successful."""
        ...

    @abstractmethod
    def is_error(self) -> bool:
        """Check if the operation failed."""
        ...

    def is_partial(self) -> bool:
        """Check if the operation partially succeeded."""
        return self.status == ResultStatus.PARTIAL

    @abstractmethod
    def unwrap(self) -> T:
        """Get the result data.

        Returns:
            The result data if successful

        Raises:
            ResultError: If the result is an error
        """
        ...

    def unwrap_or(self, default: T) -> T:
        """Get the result data or a default value.

        Args:
            default: Value to return if result is an error

        Returns:
            The result data if successful, otherwise the default
        """
        try:
            return self.unwrap()
        except ResultError:
            return default

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata.to_dict(),
        }

    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class SuccessResult(AgentResult[T]):
    """Result type for successful operations.

    Contains the operation data and success metadata.

    Attributes:
        data: The result data from the operation
        artifacts: Optional list of generated artifacts (file paths, etc.)
    """

    data: T = None  # type: ignore[assignment]
    artifacts: list[str] = field(default_factory=list)
    status: ResultStatus = field(default=ResultStatus.SUCCESS, init=False)

    def is_success(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.data

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["data"] = self.data
        base["artifacts"] = self.artifacts
        return base


@dataclass
class ErrorResult(AgentResult[T]):
    """Result type for failed operations.

    Contains error details and recovery information.

    Attributes:
        error_code: Machine-readable error code
        error_type: Exception type name
        stack_trace: Optional stack trace for debugging
        recoverable: Whether the error can be retried
        recovery_hint: Suggestion for recovery
    """

    error_code: str = "UNKNOWN_ERROR"
    error_type: str = "Error"
    stack_trace: str | None = None
    recoverable: bool = False
    recovery_hint: str | None = None
    status: ResultStatus = field(default=ResultStatus.ERROR, init=False)

    def is_success(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise ResultError(
            code=self.error_code,
            message=self.message,
            error_type=self.error_type,
            recoverable=self.recoverable,
        )

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "error_code": self.error_code,
                "error_type": self.error_type,
                "stack_trace": self.stack_trace,
                "recoverable": self.recoverable,
                "recovery_hint": self.recovery_hint,
            }
        )
        return base

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        recoverable: bool = False,
        recovery_hint: str | None = None,
    ) -> "ErrorResult":
        """Create an ErrorResult from an exception.

        Args:
            exception: The exception that occurred
            recoverable: Whether the operation can be retried
            recovery_hint: Suggestion for recovery

        Returns:
            ErrorResult with exception details
        """
        import traceback

        return cls(
            message=str(exception),
            error_code=type(exception).__name__.upper(),
            error_type=type(exception).__name__,
            stack_trace=traceback.format_exc(),
            recoverable=recoverable,
            recovery_hint=recovery_hint,
        )


@dataclass
class PartialResult(AgentResult[T]):
    """Result type for partially successful operations.

    Used when an operation completes some work but encounters issues.

    Attributes:
        data: The partial result data
        completed_items: Number of items successfully processed
        total_items: Total number of items to process
        errors: List of errors encountered
    """

    data: T = None  # type: ignore[assignment]
    completed_items: int = 0
    total_items: int = 0
    errors: list[str] = field(default_factory=list)
    status: ResultStatus = field(default=ResultStatus.PARTIAL, init=False)

    def is_success(self) -> bool:
        return False

    def is_error(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.data

    @property
    def completion_ratio(self) -> float:
        """Get the completion ratio (0.0 to 1.0)."""
        if self.total_items == 0:
            return 0.0
        return self.completed_items / self.total_items

    @property
    def completion_percentage(self) -> int:
        """Get the completion percentage (0 to 100)."""
        return int(self.completion_ratio * 100)

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "data": self.data,
                "completed_items": self.completed_items,
                "total_items": self.total_items,
                "completion_percentage": self.completion_percentage,
                "errors": self.errors,
            }
        )
        return base


# ═══════════════════════════════════════════════════════════════════════════
# RESULT EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════


class ResultError(Exception):
    """Exception raised when unwrapping an error result."""

    def __init__(
        self,
        code: str,
        message: str,
        error_type: str = "Error",
        recoverable: bool = False,
    ):
        self.code = code
        self.error_type = error_type
        self.recoverable = recoverable
        super().__init__(f"[{code}] {message}")


# ═══════════════════════════════════════════════════════════════════════════
# ERROR CODES
# Standardized error codes for agent operations
# ═══════════════════════════════════════════════════════════════════════════


class ErrorCode:
    """Standardized error codes for agent operations."""

    # General Errors
    UNKNOWN_ERROR: Final[str] = "UNKNOWN_ERROR"
    INVALID_INPUT: Final[str] = "INVALID_INPUT"
    TIMEOUT: Final[str] = "TIMEOUT"
    CANCELLED: Final[str] = "CANCELLED"

    # Agent Errors
    AGENT_NOT_FOUND: Final[str] = "AGENT_NOT_FOUND"
    AGENT_UNAVAILABLE: Final[str] = "AGENT_UNAVAILABLE"
    AGENT_ERROR: Final[str] = "AGENT_ERROR"
    AGENT_TIMEOUT: Final[str] = "AGENT_TIMEOUT"

    # Task Errors
    TASK_NOT_FOUND: Final[str] = "TASK_NOT_FOUND"
    TASK_FAILED: Final[str] = "TASK_FAILED"
    TASK_CANCELLED: Final[str] = "TASK_CANCELLED"

    # Resource Errors
    RESOURCE_NOT_FOUND: Final[str] = "RESOURCE_NOT_FOUND"
    RESOURCE_LOCKED: Final[str] = "RESOURCE_LOCKED"
    RESOURCE_EXHAUSTED: Final[str] = "RESOURCE_EXHAUSTED"

    # Permission Errors
    PERMISSION_DENIED: Final[str] = "PERMISSION_DENIED"
    CAPABILITY_MISSING: Final[str] = "CAPABILITY_MISSING"

    # LLM Errors
    LLM_ERROR: Final[str] = "LLM_ERROR"
    LLM_RATE_LIMITED: Final[str] = "LLM_RATE_LIMITED"
    LLM_CONTEXT_EXCEEDED: Final[str] = "LLM_CONTEXT_EXCEEDED"
