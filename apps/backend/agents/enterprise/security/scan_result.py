"""Security scan result types.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..types import ScanStatus, Severity


@dataclass
class VulnerabilityFinding:
    """A security vulnerability finding."""

    id: str
    severity: Severity
    category: str
    title: str
    description: str
    line_start: int
    line_end: int | None = None
    cwe_id: str | None = None
    cve_id: str | None = None
    owasp_category: str | None = None
    remediation: str | None = None
    code_snippet: str | None = None
    confidence: float = 0.8  # 0.0 - 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "cwe_id": self.cwe_id,
            "cve_id": self.cve_id,
            "owasp_category": self.owasp_category,
            "remediation": self.remediation,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence,
        }


@dataclass
class SecretFinding:
    """A detected secret or credential."""

    id: str
    secret_type: str  # api_key, password, token, etc.
    line: int
    column_start: int | None = None
    column_end: int | None = None
    pattern_matched: str | None = None
    severity: Severity = Severity.CRITICAL
    masked_value: str | None = None
    remediation: str = "Remove the secret and rotate credentials immediately."

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "secret_type": self.secret_type,
            "line": self.line,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "pattern_matched": self.pattern_matched,
            "severity": self.severity.value,
            "masked_value": self.masked_value,
            "remediation": self.remediation,
        }


@dataclass
class ScanResult:
    """Complete security scan result."""

    scan_id: str
    target: str
    status: ScanStatus = ScanStatus.COMPLETED
    vulnerabilities: list[VulnerabilityFinding] = field(default_factory=list)
    secrets: list[SecretFinding] = field(default_factory=list)
    risk_score: float = 0.0  # 0.0 - 10.0
    recommendations: list[str] = field(default_factory=list)
    passed: bool = True
    scan_duration_seconds: float = 0.0
    scanner_id: str | None = None
    scanner_provider: str | None = None  # Which LLM provider was used
    timestamp: datetime = field(default_factory=datetime.utcnow)
    owasp_compliance: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_critical_vulnerabilities(self) -> bool:
        """Check if scan found critical vulnerabilities."""
        return any(v.severity == Severity.CRITICAL for v in self.vulnerabilities)

    @property
    def has_secrets(self) -> bool:
        """Check if scan found secrets."""
        return len(self.secrets) > 0

    @property
    def total_findings(self) -> int:
        """Get total number of findings."""
        return len(self.vulnerabilities) + len(self.secrets)

    @property
    def severity_counts(self) -> dict[str, int]:
        """Get count of findings by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for v in self.vulnerabilities:
            counts[v.severity.value] = counts.get(v.severity.value, 0) + 1
        for s in self.secrets:
            counts[s.severity.value] = counts.get(s.severity.value, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scan_id": self.scan_id,
            "target": self.target,
            "status": self.status.value,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "secrets": [s.to_dict() for s in self.secrets],
            "risk_score": self.risk_score,
            "recommendations": self.recommendations,
            "passed": self.passed,
            "scan_duration_seconds": self.scan_duration_seconds,
            "scanner_id": self.scanner_id,
            "scanner_provider": self.scanner_provider,
            "timestamp": self.timestamp.isoformat(),
            "owasp_compliance": self.owasp_compliance,
            "severity_counts": self.severity_counts,
            "total_findings": self.total_findings,
        }

    def get_summary(self) -> str:
        """Get a human-readable summary of the scan."""
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        counts = self.severity_counts
        return (
            f"{status}\n"
            f"Risk Score: {self.risk_score:.1f}/10\n"
            f"Vulnerabilities: {len(self.vulnerabilities)} "
            f"(Critical: {counts['critical']}, High: {counts['high']}, "
            f"Medium: {counts['medium']}, Low: {counts['low']})\n"
            f"Secrets Found: {len(self.secrets)}"
        )
