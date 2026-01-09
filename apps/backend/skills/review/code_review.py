"""Code review skill.

Performs comprehensive code reviews.

Capabilities:
- Review code quality
- Identify issues and bugs
- Suggest improvements
- Check style compliance
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from skills.core.base_skill import (
    BaseSkill,
    SkillCategory,
    SkillContext,
    SkillResult,
    SkillStatus,
)


class IssueSeverity(Enum):
    """Severity of review issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(Enum):
    """Category of review issues."""

    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    BEST_PRACTICE = "best_practice"


@dataclass
class ReviewIssue:
    """A code review issue."""

    title: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    suggestion: str | None = None
    code_snippet: str | None = None


@dataclass
class ReviewResult:
    """Result of code review."""

    issues: list[ReviewIssue]
    score: float  # 0-100
    summary: str
    recommendations: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH)


class CodeReviewSkill(BaseSkill):
    """Perform comprehensive code review.

    Uses LLM to analyze code and provide detailed feedback
    on quality, bugs, style, and best practices.

    Example:
        skill = CodeReviewSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def foo(x): return x",
                "file_path": "src/utils.py",
                "language": "python",
            }
        )
        result = await skill.run(context)
    """

    name = "code_review"
    description = "Perform comprehensive code review"
    category = SkillCategory.REVIEW
    required_tools = ["file_read"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute code review.

        Args:
            context: Execution context with code to review

        Returns:
            SkillResult with review findings
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        file_path = input_data.get("file_path")
        language = input_data.get("language", "unknown")

        # Perform review (placeholder for LLM)
        review = self._perform_review(code, file_path, language)

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "score": review.score,
                "summary": review.summary,
                "issues": [self._issue_to_dict(i) for i in review.issues],
                "critical_count": review.critical_count,
                "high_count": review.high_count,
                "recommendations": review.recommendations,
            },
            tokens_used=0,
        )

    def _perform_review(
        self, code: str, file_path: str | None, language: str
    ) -> ReviewResult:
        """Perform code review (placeholder)."""
        return ReviewResult(
            issues=[],
            score=80.0,
            summary="Code review completed. No major issues found.",
            recommendations=[],
        )

    def _issue_to_dict(self, issue: ReviewIssue) -> dict[str, Any]:
        """Convert ReviewIssue to dictionary."""
        return {
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity.value,
            "category": issue.category.value,
            "file_path": issue.file_path,
            "line_start": issue.line_start,
            "line_end": issue.line_end,
            "suggestion": issue.suggestion,
        }
