"""Enterprise agent type definitions.

World-Class Standards:
- Clear type hierarchy for agents
- Comprehensive capability definitions
- Structured result types for all operations

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EnterpriseAgentType(Enum):
    """Enterprise agent type enumeration."""
    CODE_REVIEW = "code_review"
    SECURITY = "security"
    QA = "qa"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATOR = "orchestrator"


class Severity(Enum):
    """Severity levels for findings and issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReviewStatus(Enum):
    """Code review status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


class ScanStatus(Enum):
    """Security scan status."""
    QUEUED = "queued"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"


class TestStatus(Enum):
    """Test execution status."""
    NOT_RUN = "not_run"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class DocstringStyle(Enum):
    """Docstring style formats."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    RESTRUCTURED = "restructured"




@dataclass
class Finding:
    """A finding from code review or security scan."""
    id: str
    severity: Severity
    category: str
    message: str
    line_start: int
    line_end: Optional[int] = None
    file_path: Optional[str] = None
    suggestion: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    remediation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Suggestion:
    """A code improvement suggestion."""
    id: str
    title: str
    description: str
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    original_code: Optional[str] = None
    suggested_code: Optional[str] = None
    category: str = "improvement"
    priority: Severity = Severity.INFO


@dataclass
class CodeReviewResult:
    """Structured code review result."""
    file_path: str
    findings: List[Finding] = field(default_factory=list)
    suggestions: List[Suggestion] = field(default_factory=list)
    severity_counts: Dict[str, int] = field(default_factory=dict)
    overall_quality: float = 0.0  # 0.0 - 1.0
    approved: bool = False
    review_time_seconds: float = 0.0
    reviewer_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityScanResult:
    """Security scan results."""
    scan_id: str
    target: str
    status: ScanStatus = ScanStatus.COMPLETED
    vulnerabilities: List[Finding] = field(default_factory=list)
    secrets_found: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0  # 0.0 - 10.0
    recommendations: List[str] = field(default_factory=list)
    passed: bool = True
    scan_duration_seconds: float = 0.0
    scanner_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    owasp_compliance: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """A generated test case."""
    id: str
    name: str
    description: str
    test_type: str  # unit, integration, e2e
    target_function: str
    test_code: str
    assertions: List[str] = field(default_factory=list)
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    expected_result: Optional[Any] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class TestGenerationResult:
    """Test generation result."""
    target_file: str
    test_cases: List[TestCase] = field(default_factory=list)
    coverage_estimate: float = 0.0  # Estimated coverage percentage
    framework: str = "pytest"
    test_file_path: Optional[str] = None
    generation_time_seconds: float = 0.0
    generator_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CoverageAnalysis:
    """Code coverage analysis result."""
    total_lines: int = 0
    covered_lines: int = 0
    coverage_percentage: float = 0.0
    uncovered_lines: List[int] = field(default_factory=list)
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    file_coverage: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DocumentationResult:
    """Documentation generation result."""
    doc_type: str  # docstring, readme, api_doc, changelog
    content: str
    format: str = "markdown"
    file_path: Optional[str] = None
    sections: List[Dict[str, Any]] = field(default_factory=list)
    generation_time_seconds: float = 0.0
    generator_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProjectAnalysis:
    """Project analysis result."""
    project_path: str
    language_distribution: Dict[str, float] = field(default_factory=dict)
    file_count: int = 0
    total_lines: int = 0
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    architecture_type: Optional[str] = None
    tech_debt_score: float = 0.0  # 0.0 - 10.0
    complexity_score: float = 0.0
    health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    analysis_time_seconds: float = 0.0
    analyzer_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PipelineStage:
    """A stage in an agent pipeline."""
    stage_id: str
    agent_type: EnterpriseAgentType
    agent_config: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)  # References to previous stage outputs
    timeout_seconds: int = 300
    retry_count: int = 3
    fail_fast: bool = True


@dataclass
class Pipeline:
    """Agent pipeline definition."""
    pipeline_id: str
    name: str
    stages: List[PipelineStage] = field(default_factory=list)
    parallel: bool = False
    fail_fast: bool = True
    timeout_seconds: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Pipeline execution result."""
    pipeline_id: str
    status: str  # success, failure, partial
    stage_results: Dict[str, Any] = field(default_factory=dict)
    total_duration_seconds: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    sender_id: str
    receiver_id: str
    message_type: str  # request, response, notification, error
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # Higher = more urgent
    ttl_seconds: int = 300


# OWASP Top 10 2021 Categories
OWASP_CATEGORIES: Dict[str, str] = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)",
}


# Supported test frameworks by language
TEST_FRAMEWORKS: Dict[str, List[str]] = {
    "python": ["pytest", "unittest", "nose2"],
    "javascript": ["jest", "mocha", "vitest"],
    "typescript": ["jest", "vitest", "mocha"],
    "java": ["junit", "testng"],
    "go": ["testing", "testify"],
    "rust": ["cargo-test"],
}
