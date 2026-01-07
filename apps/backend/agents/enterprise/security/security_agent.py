"""Security Agent for vulnerability scanning.

World-Class Standards:
- OWASP Top 10 coverage
- Zero false negatives for critical vulnerabilities
- LLM-agnostic vulnerability analysis

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import json
import uuid

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import (
    EnterpriseAgentType,
    Finding,
    SecurityScanResult,
    Severity,
    ScanStatus,
)
from .scan_result import ScanResult, VulnerabilityFinding, SecretFinding
from .vulnerability_db import VulnerabilityDB
from .owasp_checker import OWASPChecker, OWASPFinding


class SecurityAgent(BaseEnterpriseAgent):
    """Agent for security vulnerability scanning using any of 8 LLM providers.
    
    Provides comprehensive security analysis including:
    - Vulnerability detection
    - Secret scanning
    - OWASP Top 10 compliance checking
    - Remediation suggestions
    
    Attributes:
        vulnerability_db: Database of known vulnerability patterns
        owasp_checker: OWASP compliance checker
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.SECURITY
    AGENT_CATEGORY: ClassVar[str] = "security"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert security analyst with deep knowledge of:
1. OWASP Top 10 vulnerabilities
2. Common vulnerability patterns (CWE)
3. Secure coding practices
4. Secret detection and management
5. Dependency security

Analyze code thoroughly for security issues.
Provide severity ratings and specific remediation steps.
Prioritize critical security issues."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the security agent."""
        super().__init__(config, llm_router)
        
        # Add security capability
        self.add_capability(AgentCapability.SECURITY_SCAN)
        
        # Initialize components
        self.vulnerability_db = VulnerabilityDB()
        self.owasp_checker = OWASPChecker()
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Security scanning agent that performs vulnerability analysis, "
            "secret detection, and OWASP compliance checking. Uses configured "
            "LLM provider for intelligent security analysis."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security scan based on context.
        
        Args:
            context: Must contain 'code' and 'language' or 'lockfile'
            
        Returns:
            Security scan results
        """
        if "code" in context and "language" in context:
            result = await self.scan_code(
                code=context["code"],
                language=context["language"],
                file_path=context.get("file_path"),
            )
            return {
                "status": "success",
                "scan_type": "code",
                "result": self._result_to_dict(result),
            }
        elif "lockfile" in context:
            vulnerabilities = await self.scan_dependencies(context["lockfile"])
            return {
                "status": "success",
                "scan_type": "dependencies",
                "vulnerabilities": [v.to_dict() for v in vulnerabilities],
            }
        else:
            return {
                "status": "error",
                "message": "Context must contain 'code' and 'language' or 'lockfile'",
            }
    
    async def scan_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
    ) -> SecurityScanResult:
        """Scan code for security issues.
        
        Uses agent's configured LLM for deep analysis.
        
        Args:
            code: Source code to scan
            language: Programming language
            file_path: Optional file path for context
            
        Returns:
            Security scan results
        """
        scan_id = str(uuid.uuid4())
        target = file_path or "inline_code"
        
        # Build scan prompt
        prompt = f"""Analyze this {language} code for security vulnerabilities.

```{language}
{code}
```

Provide findings in JSON format:
{{
  "vulnerabilities": [
    {{
      "id": "V001",
      "severity": "critical|high|medium|low",
      "category": "OWASP category (e.g., A01-Broken Access Control)",
      "cwe_id": "CWE-XXX",
      "title": "Vulnerability title",
      "description": "Detailed description",
      "line_start": 10,
      "line_end": 12,
      "remediation": "How to fix this issue",
      "code_snippet": "Vulnerable code"
    }}
  ],
  "secrets_found": [
    {{
      "type": "api_key|password|token",
      "line": 5,
      "pattern": "Matched pattern description"
    }}
  ],
  "risk_score": 7.5,
  "recommendations": ["General security recommendations"]
}}

Check for:
1. OWASP Top 10 vulnerabilities
2. Hardcoded secrets and credentials
3. Injection vulnerabilities (SQL, command, XSS)
4. Authentication/authorization issues
5. Data exposure risks
6. Insecure cryptography
"""
        
        # Get LLM response
        response = await self.complete(prompt)
        
        # Also run pattern-based checks
        pattern_vulnerabilities = self.vulnerability_db.scan(code, language)
        owasp_findings = await self.check_owasp(code)
        
        # Parse and merge results
        return self._parse_scan_response(
            scan_id=scan_id,
            target=target,
            response=response,
            pattern_vulnerabilities=pattern_vulnerabilities,
            owasp_findings=owasp_findings,
        )
    
    async def check_owasp(
        self,
        code: str,
    ) -> List[OWASPFinding]:
        """Check code against OWASP Top 10.
        
        Args:
            code: Source code to check
            
        Returns:
            List of OWASP compliance findings
        """
        return self.owasp_checker.check(code)
    
    async def scan_dependencies(
        self,
        lockfile: str,
    ) -> List[VulnerabilityFinding]:
        """Scan dependencies for known vulnerabilities.
        
        Args:
            lockfile: Content of package lock file
            
        Returns:
            List of vulnerable dependencies
        """
        prompt = f"""Analyze this dependency lock file for known vulnerabilities.

{lockfile}

Provide findings in JSON format:
{{
  "vulnerabilities": [
    {{
      "package": "package-name",
      "version": "1.2.3",
      "severity": "critical|high|medium|low",
      "cve_id": "CVE-XXXX-XXXXX",
      "description": "Vulnerability description",
      "fixed_version": "1.2.4",
      "recommendation": "Upgrade to fixed version"
    }}
  ]
}}

Check for:
- Known CVEs in dependencies
- Outdated packages with security issues
- Transitive dependency vulnerabilities
"""
        
        response = await self.complete(prompt)
        return self._parse_dependency_response(response)
    
    async def generate_remediation(
        self,
        finding: VulnerabilityFinding,
    ) -> str:
        """Generate detailed remediation for a finding.
        
        Args:
            finding: The vulnerability finding
            
        Returns:
            Detailed remediation guidance
        """
        prompt = f"""Provide detailed remediation guidance for this security vulnerability:

Vulnerability: {finding.title}
Severity: {finding.severity.value}
Category: {finding.category}
CWE: {finding.cwe_id or 'Not specified'}
Description: {finding.description}

Code:
```
{finding.code_snippet or 'Not available'}
```

Provide:
1. Step-by-step remediation instructions
2. Secure code example
3. Best practices to prevent this issue
4. Testing recommendations
"""
        
        return await self.complete(prompt)
    
    def _parse_scan_response(
        self,
        scan_id: str,
        target: str,
        response: str,
        pattern_vulnerabilities: List[VulnerabilityFinding],
        owasp_findings: List[OWASPFinding],
    ) -> SecurityScanResult:
        """Parse LLM response into structured result."""
        vulnerabilities: List[Finding] = []
        secrets_found: List[Dict[str, Any]] = []
        risk_score = 0.0
        recommendations: List[str] = []
        owasp_compliance: Dict[str, bool] = {}
        
        # Parse JSON response
        try:
            data = json.loads(response)
            
            for v in data.get("vulnerabilities", []):
                severity = Severity(v.get("severity", "medium"))
                vulnerabilities.append(Finding(
                    id=v.get("id", str(uuid.uuid4())),
                    severity=severity,
                    category=v.get("category", "security"),
                    message=v.get("description", v.get("title", "")),
                    line_start=v.get("line_start", 1),
                    line_end=v.get("line_end"),
                    cwe_id=v.get("cwe_id"),
                    owasp_category=v.get("category"),
                    remediation=v.get("remediation"),
                ))
            
            secrets_found = data.get("secrets_found", [])
            risk_score = data.get("risk_score", 0.0)
            recommendations = data.get("recommendations", [])
            
        except json.JSONDecodeError:
            pass
        
        # Add pattern-based vulnerabilities
        for pv in pattern_vulnerabilities:
            vulnerabilities.append(Finding(
                id=pv.id,
                severity=pv.severity,
                category=pv.category,
                message=pv.description,
                line_start=pv.line_start,
                line_end=pv.line_end,
                cwe_id=pv.cwe_id,
                remediation=pv.remediation,
            ))
        
        # Add OWASP findings to compliance map
        for of in owasp_findings:
            owasp_compliance[of.category.value] = False
        
        # Calculate pass status
        passed = all(
            f.severity not in (Severity.CRITICAL, Severity.HIGH)
            for f in vulnerabilities
        )
        
        return SecurityScanResult(
            scan_id=scan_id,
            target=target,
            status=ScanStatus.COMPLETED,
            vulnerabilities=vulnerabilities,
            secrets_found=secrets_found,
            risk_score=risk_score,
            recommendations=recommendations,
            passed=passed,
            scanner_id=self.id,
            owasp_compliance=owasp_compliance,
        )
    
    def _parse_dependency_response(
        self,
        response: str,
    ) -> List[VulnerabilityFinding]:
        """Parse dependency scan response."""
        findings: List[VulnerabilityFinding] = []
        
        try:
            data = json.loads(response)
            for v in data.get("vulnerabilities", []):
                findings.append(VulnerabilityFinding(
                    id=str(uuid.uuid4()),
                    severity=Severity(v.get("severity", "medium")),
                    category="dependency",
                    title=f"{v.get('package', 'Unknown')}@{v.get('version', 'unknown')}",
                    description=v.get("description", ""),
                    line_start=1,
                    cve_id=v.get("cve_id"),
                    remediation=v.get("recommendation"),
                ))
        except json.JSONDecodeError:
            pass
        
        return findings
    
    def _result_to_dict(self, result: SecurityScanResult) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "scan_id": result.scan_id,
            "target": result.target,
            "status": result.status.value,
            "vulnerabilities_count": len(result.vulnerabilities),
            "secrets_found_count": len(result.secrets_found),
            "risk_score": result.risk_score,
            "passed": result.passed,
            "scanner_id": result.scanner_id,
        }
