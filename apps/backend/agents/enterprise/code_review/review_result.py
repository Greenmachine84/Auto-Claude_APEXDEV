"""Review result types for code review agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..types import Severity


@dataclass
class ReviewFinding:
    """A finding from code review.

    Represents an issue, warning, or suggestion found during review.
    """

    id: str
    severity: Severity
    category: str
    message: str
    line_start: int
    line_end: int | None = None
    column_start: int | None = None
    column_end: int | None = None
    suggestion: str | None = None
    code_snippet: str | None = None
    rule_id: str | None = None
    documentation_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "rule_id": self.rule_id,
            "documentation_url": self.documentation_url,
        }


@dataclass
class ReviewSuggestion:
    """A code improvement suggestion.

    Contains original and suggested code with explanation.
    """

    id: str
    title: str
    description: str
    line_start: int
    line_end: int | None = None
    original_code: str | None = None
    suggested_code: str | None = None
    category: str = "improvement"
    priority: Severity = Severity.INFO
    effort_estimate: str = "low"  # low, medium, high

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "category": self.category,
            "priority": self.priority.value,
            "effort_estimate": self.effort_estimate,
        }


@dataclass
class ReviewResult:
    """Complete review result for a file or PR.

    Contains all findings, suggestions, and quality metrics.
    """

    file_path: str
    findings: list[ReviewFinding] = field(default_factory=list)
    suggestions: list[ReviewSuggestion] = field(default_factory=list)
    severity_counts: dict[str, int] = field(default_factory=dict)
    overall_quality: float = 0.0  # 0.0 - 1.0
    approved: bool = False
    review_time_seconds: float = 0.0
    lines_reviewed: int = 0
    reviewer_id: str | None = None
    reviewer_provider: str | None = None  # Which LLM provider was used
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize severity counts if not provided."""
        if not self.severity_counts:
            self.severity_counts = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

    @property
    def has_critical_issues(self) -> bool:
        """Check if review has critical issues."""
        return self.severity_counts.get("critical", 0) > 0

    @property
    def has_blocking_issues(self) -> bool:
        """Check if review has blocking issues (critical or high)."""
        return (
            self.severity_counts.get("critical", 0) > 0
            or self.severity_counts.get("high", 0) > 0
        )

    @property
    def total_findings(self) -> int:
        """Get total number of findings."""
        return len(self.findings)

    @property
    def total_suggestions(self) -> int:
        """Get total number of suggestions."""
        return len(self.suggestions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "findings": [f.to_dict() for f in self.findings],
            "suggestions": [s.to_dict() for s in self.suggestions],
            "severity_counts": self.severity_counts,
            "overall_quality": self.overall_quality,
            "approved": self.approved,
            "review_time_seconds": self.review_time_seconds,
            "lines_reviewed": self.lines_reviewed,
            "reviewer_id": self.reviewer_id,
            "reviewer_provider": self.reviewer_provider,
            "timestamp": self.timestamp.isoformat(),
            "has_critical_issues": self.has_critical_issues,
            "has_blocking_issues": self.has_blocking_issues,
            "total_findings": self.total_findings,
            "total_suggestions": self.total_suggestions,
        }

    def get_summary(self) -> str:
        """Get a human-readable summary of the review."""
        status = "✅ APPROVED" if self.approved else "❌ CHANGES REQUESTED"
        return (
            f"{status}\n"
            f"Quality Score: {self.overall_quality:.1%}\n"
            f"Findings: {self.total_findings} "
            f"(Critical: {self.severity_counts.get('critical', 0)}, "
            f"High: {self.severity_counts.get('high', 0)}, "
            f"Medium: {self.severity_counts.get('medium', 0)}, "
            f"Low: {self.severity_counts.get('low', 0)})\n"
            f"Suggestions: {self.total_suggestions}"
        )
