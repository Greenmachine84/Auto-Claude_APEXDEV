"""Security review skill.

Performs security-focused code review.

Capabilities:
- Identify security vulnerabilities
- Check for common security issues
- OWASP Top 10 analysis
- Suggest security improvements
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


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""

    INJECTION = "injection"
    XSS = "xss"
    BROKEN_AUTH = "broken_auth"
    SENSITIVE_DATA = "sensitive_data"
    XXE = "xxe"
    BROKEN_ACCESS = "broken_access"
    SECURITY_MISCONFIG = "security_misconfig"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    INSUFFICIENT_LOGGING = "insufficient_logging"
    HARDCODED_SECRETS = "hardcoded_secrets"
    PATH_TRAVERSAL = "path_traversal"


@dataclass
class SecurityFinding:
    """A security vulnerability finding."""

    title: str
    description: str
    vulnerability_type: VulnerabilityType
    severity: str  # critical, high, medium, low
    cwe_id: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    remediation: str | None = None
    references: list[str] = field(default_factory=list)


class SecurityReviewSkill(BaseSkill):
    """Perform security-focused code review.

    Analyzes code for security vulnerabilities using OWASP
    guidelines and security best practices.

    Example:
        skill = SecurityReviewSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "password = request.args.get('pwd')",
                "language": "python",
            }
        )
        result = await skill.run(context)
    """

    name = "security_review"
    description = "Security-focused code review"
    category = SkillCategory.REVIEW
    required_tools = ["file_read"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    # Common vulnerability patterns
    VULNERABILITY_PATTERNS = {
        "python": [
            (r"eval\s*\(", VulnerabilityType.INJECTION),
            (r"exec\s*\(", VulnerabilityType.INJECTION),
            (r"pickle\.loads", VulnerabilityType.INSECURE_DESERIALIZATION),
            (
                r'password\s*=\s*["\x27][^"\x27]+["\x27]',
                VulnerabilityType.HARDCODED_SECRETS,
            ),
        ],
        "javascript": [
            (r"innerHTML\s*=", VulnerabilityType.XSS),
            (r"eval\s*\(", VulnerabilityType.INJECTION),
            (r"document\.write", VulnerabilityType.XSS),
        ],
    }

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute security review.

        Args:
            context: Execution context with code to review

        Returns:
            SkillResult with security findings
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        language = input_data.get("language", "python")

        # Perform security analysis
        findings = self._analyze_security(code, language)

        # Calculate security score
        score = self._calculate_score(findings)

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "security_score": score,
                "findings": [self._finding_to_dict(f) for f in findings],
                "finding_count": len(findings),
                "critical_count": sum(1 for f in findings if f.severity == "critical"),
                "high_count": sum(1 for f in findings if f.severity == "high"),
            },
            tokens_used=0,
        )

    def _analyze_security(self, code: str, language: str) -> list[SecurityFinding]:
        """Analyze code for security issues."""
        findings = []
        # Placeholder - will use pattern matching and LLM
        return findings

    def _calculate_score(self, findings: list[SecurityFinding]) -> float:
        """Calculate security score (0-100)."""
        if not findings:
            return 100.0

        deductions = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
        }

        total_deduction = sum(deductions.get(f.severity, 0) for f in findings)

        return max(0.0, 100.0 - total_deduction)

    def _finding_to_dict(self, finding: SecurityFinding) -> dict[str, Any]:
        """Convert SecurityFinding to dictionary."""
        return {
            "title": finding.title,
            "description": finding.description,
            "vulnerability_type": finding.vulnerability_type.value,
            "severity": finding.severity,
            "cwe_id": finding.cwe_id,
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "remediation": finding.remediation,
        }
