"""Reviewer Agent.

Code review and validation agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Responsibilities:
- Code review
- Quality validation
- Security scanning
- Best practices enforcement
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar

from ..base import (
    AgentConfig,
    BaseAgent,
    ExecutionContext,
)
from ..base.agent_hooks import HookType
from ..types import AgentResult, AgentType, ErrorCode, ErrorResult, SuccessResult

logger = logging.getLogger(__name__)


class FindingSeverity(Enum):
    """Severity levels for review findings."""

    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFO = auto()


class FindingCategory(Enum):
    """Categories for review findings."""

    SECURITY = auto()
    PERFORMANCE = auto()
    MAINTAINABILITY = auto()
    CORRECTNESS = auto()
    STYLE = auto()
    DOCUMENTATION = auto()
    BEST_PRACTICE = auto()


@dataclass
class ReviewFinding:
    """A single review finding."""

    message: str
    severity: FindingSeverity
    category: FindingCategory
    file_path: str | None = None
    line_number: int | None = None
    suggestion: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "severity": self.severity.name,
            "category": self.category.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


@dataclass
class ReviewResult:
    """Result of a code review."""

    approved: bool
    findings: list[ReviewFinding] = field(default_factory=list)
    summary: str = ""
    reviewed_files: list[str] = field(default_factory=list)
    score: float = 0.0  # 0-100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "approved": self.approved,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "reviewed_files": self.reviewed_files,
            "score": self.score,
            "finding_counts": {
                severity.name: sum(1 for f in self.findings if f.severity == severity)
                for severity in FindingSeverity
            },
        }


class ReviewerAgent(BaseAgent):
    """Code review and validation agent.

    The Reviewer agent analyzes code for quality, security, and best practices.
    It operates in read-only mode and does not modify files.

    Capabilities:
    - Read files for analysis
    - Analyze code structure
    - Call LLM for review
    - Access memory for context

    Usage:
        >>> reviewer = ReviewerAgent()
        >>> reviewer.initialize()
        >>> result = reviewer.run(context)
    """

    AGENT_TYPE: ClassVar[AgentType] = AgentType.REVIEWER

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
    ):
        """Initialize reviewer agent.

        Args:
            config: Agent configuration
            agent_id: Optional agent identifier
        """
        if config is None:
            config = AgentConfig.for_reviewer()
        super().__init__(config=config, agent_id=agent_id)

        self._review_history: list[ReviewResult] = []

    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Code review agent that analyzes code for quality, security, "
            "and adherence to best practices. Provides detailed findings "
            "and suggestions for improvement."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute code review task.

        Args:
            context: Execution context with task details

        Returns:
            AgentResult with ReviewResult data
        """
        self._logger.info(f"Reviewer executing task: {context.task}")

        try:
            self._hooks.execute(
                HookType.ON_TASK_START,
                metadata={"task_id": context.task.task_id if context.task else None},
            )

            # Perform review
            review_result = self._perform_review(context)
            self._review_history.append(review_result)

            self._hooks.execute(
                HookType.ON_TASK_COMPLETE,
                result=review_result,
            )

            return SuccessResult(
                data=review_result.to_dict(),
                message=f"Review completed: {'Approved' if review_result.approved else 'Changes Requested'}",
                metadata={
                    "score": review_result.score,
                    "finding_count": len(review_result.findings),
                },
            )

        except Exception as e:
            self._logger.error(f"Reviewer execution failed: {e}")
            return ErrorResult(
                message=str(e),
                code=ErrorCode.EXECUTION_ERROR,
                recoverable=True,
            )

    def _perform_review(self, context: ExecutionContext) -> ReviewResult:
        """Perform the code review.

        Args:
            context: Execution context

        Returns:
            ReviewResult with findings
        """
        # Placeholder - in production this integrates with LLM
        return ReviewResult(
            approved=True,
            summary="Code review completed",
            score=85.0,
        )

    def review_file(
        self,
        file_path: str,
        context: ExecutionContext,
    ) -> list[ReviewFinding]:
        """Review a single file.

        Args:
            file_path: Path to file
            context: Execution context

        Returns:
            List of findings
        """
        # Placeholder
        return []

    def check_security(
        self,
        file_path: str,
        context: ExecutionContext,
    ) -> list[ReviewFinding]:
        """Check file for security issues.

        Args:
            file_path: Path to file
            context: Execution context

        Returns:
            Security-related findings
        """
        # Placeholder
        return []

    def get_stats(self) -> dict[str, Any]:
        """Get reviewer statistics."""
        total_reviews = len(self._review_history)
        approved_count = sum(1 for r in self._review_history if r.approved)

        return {
            **self.to_dict(),
            "total_reviews": total_reviews,
            "approval_rate": approved_count / total_reviews if total_reviews > 0 else 0,
            "average_score": (
                sum(r.score for r in self._review_history) / total_reviews
                if total_reviews > 0
                else 0
            ),
        }
