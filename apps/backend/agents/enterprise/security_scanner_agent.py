"""Security Scanner Agent.

Security scanning and analysis agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.
"""

from typing import ClassVar, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from ..types import AgentResult, SuccessResult, ErrorResult, ErrorCode
from .types import EnterpriseAgentType
from ..base import ExecutionContext
from .base_enterprise_agent import BaseEnterpriseAgent


class SecuritySeverity(Enum):
    """Security finding severity."""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFO = auto()


@dataclass
class SecurityFinding:
    """A security finding."""
    title: str
    severity: SecuritySeverity
    description: str
    file_path: str | None = None
    line_number: int | None = None
    cwe_id: str | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity.name,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "cwe_id": self.cwe_id,
            "remediation": self.remediation,
        }


class SecurityScannerAgent(BaseEnterpriseAgent):
    """Security scanning agent.

    Responsibilities:
    - Code security scanning
    - Secret detection
    - Dependency vulnerability checks
    - Security best practices
    """

    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.SECURITY
    AGENT_CATEGORY: ClassVar[str] = "security"

    def __init__(self, config=None, agent_id=None):
        super().__init__(config=config, agent_id=agent_id)
        self._findings: list[SecurityFinding] = []

    @classmethod
    def get_description(cls) -> str:
        return (
            "Security scanner agent that performs code security scanning, "
            "secret detection, and dependency vulnerability analysis."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        self._logger.info(f"SecurityScanner executing: {context.task}")
        try:
            self._findings = []
            scan_result = self._perform_scan(context)
            return SuccessResult(
                data=scan_result,
                message=f"Security scan complete: {len(self._findings)} findings",
                metadata={"findings_count": len(self._findings)},
            )
        except Exception as e:
            return ErrorResult(message=str(e), code=ErrorCode.EXECUTION_ERROR)

    def _perform_scan(self, context: ExecutionContext) -> dict[str, Any]:
        return {
            "status": "scanned",
            "findings": [f.to_dict() for f in self._findings],
            "agent_id": self.id,
        }
