"""Skill result types and error handling.

Defines:
- SkillResult: Result from skill execution
- SkillError: Error information
- ValidationResult: Input/output validation result
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from skills.types.skill_types import SkillStatus

T = TypeVar("T")


class ErrorSeverity(Enum):
    """Error severity levels."""

    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SkillError:
    """Error information from skill execution."""

    code: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    details: dict[str, Any] | None = None
    stack_trace: str | None = None
    recoverable: bool = False
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "stack_trace": self.stack_trace,
            "recoverable": self.recoverable,
            "suggestions": self.suggestions,
        }

    @classmethod
    def from_exception(cls, exc: Exception, code: str = "EXCEPTION") -> "SkillError":
        """Create from exception."""
        import traceback

        return cls(
            code=code,
            message=str(exc),
            severity=ErrorSeverity.ERROR,
            stack_trace=traceback.format_exc(),
            recoverable=False,
        )


@dataclass
class ValidationResult:
    """Result from input/output validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0

    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge with another validation result."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
        )

    @classmethod
    def success(cls) -> "ValidationResult":
        """Create successful validation result."""
        return cls(valid=True)

    @classmethod
    def failure(cls, error: str) -> "ValidationResult":
        """Create failed validation result."""
        return cls(valid=False, errors=[error])


@dataclass
class SkillResult(Generic[T]):
    """Result from skill execution.

    Generic type T represents the output data type.
    """

    skill_name: str
    status: SkillStatus
    output: T | None = None
    error: SkillError | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if skill completed successfully."""
        return self.status == SkillStatus.COMPLETED and self.error is None

    @property
    def failed(self) -> bool:
        """Check if skill failed."""
        return self.status in (SkillStatus.FAILED, SkillStatus.TIMEOUT)

    @property
    def duration_seconds(self) -> float | None:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def error_message(self) -> str | None:
        """Get error message if present."""
        return self.error.message if self.error else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "skill_name": self.skill_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error.to_dict() if self.error else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "metadata": self.metadata,
        }

    @classmethod
    def success_result(
        cls,
        skill_name: str,
        output: T,
        tokens_used: int = 0,
    ) -> "SkillResult[T]":
        """Create successful result."""
        return cls(
            skill_name=skill_name,
            status=SkillStatus.COMPLETED,
            output=output,
            tokens_used=tokens_used,
        )

    @classmethod
    def failure_result(
        cls,
        skill_name: str,
        error: SkillError,
    ) -> "SkillResult[T]":
        """Create failed result."""
        return cls(
            skill_name=skill_name,
            status=SkillStatus.FAILED,
            error=error,
        )

    @classmethod
    def timeout_result(
        cls,
        skill_name: str,
        timeout_seconds: int,
    ) -> "SkillResult[T]":
        """Create timeout result."""
        return cls(
            skill_name=skill_name,
            status=SkillStatus.TIMEOUT,
            error=SkillError(
                code="TIMEOUT",
                message=f"Skill timed out after {timeout_seconds} seconds",
                severity=ErrorSeverity.ERROR,
                recoverable=True,
            ),
        )
