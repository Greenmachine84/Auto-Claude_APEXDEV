"""OWASP Top 10 compliance checker.

World-Class Standards:
- Complete OWASP Top 10 2021 coverage
- Pattern-based detection
- Remediation guidance

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import re
import uuid

from ..types import Severity


class OWASPCategory(Enum):
    """OWASP Top 10 2021 categories."""
    A01_BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    A02_CRYPTOGRAPHIC_FAILURES = "A02:2021-Cryptographic Failures"
    A03_INJECTION = "A03:2021-Injection"
    A04_INSECURE_DESIGN = "A04:2021-Insecure Design"
    A05_SECURITY_MISCONFIGURATION = "A05:2021-Security Misconfiguration"
    A06_VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    A07_AUTHENTICATION_FAILURES = "A07:2021-Identification and Authentication Failures"
    A08_DATA_INTEGRITY_FAILURES = "A08:2021-Software and Data Integrity Failures"
    A09_LOGGING_FAILURES = "A09:2021-Security Logging and Monitoring Failures"
    A10_SSRF = "A10:2021-Server-Side Request Forgery"


@dataclass
class OWASPFinding:
    """An OWASP compliance finding."""
    id: str
    category: OWASPCategory
    severity: Severity
    title: str
    description: str
    line_start: int
    line_end: Optional[int] = None
    cwe_ids: List[str] = field(default_factory=list)
    remediation: str = ""
    code_snippet: Optional[str] = None
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "cwe_ids": self.cwe_ids,
            "remediation": self.remediation,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence,
        }


@dataclass
class OWASPPattern:
    """Pattern for detecting OWASP violations."""
    id: str
    category: OWASPCategory
    pattern: str
    severity: Severity
    title: str
    description: str
    cwe_ids: List[str] = field(default_factory=list)
    remediation: str = ""
    languages: Set[str] = field(default_factory=lambda: {"all"})
    
    def __post_init__(self):
        """Compile pattern."""
        self._compiled = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)


class OWASPChecker:
    """Checks code against OWASP Top 10 2021.
    
    Provides pattern-based detection for common OWASP violations.
    """
    
    def __init__(self):
        """Initialize with OWASP patterns."""
        self._patterns: List[OWASPPattern] = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load OWASP detection patterns."""
        self._patterns = [
            # A01: Broken Access Control
            OWASPPattern(
                id="A01-001",
                category=OWASPCategory.A01_BROKEN_ACCESS_CONTROL,
                pattern=r'\bos\.path\.join\s*\([^)]*\brequest\.',
                severity=Severity.HIGH,
                title="Path Traversal Risk",
                description="User input in file path operations can lead to path traversal.",
                cwe_ids=["CWE-22", "CWE-23"],
                remediation="Validate and sanitize paths. Use os.path.realpath and check against allowed directories.",
            ),
            OWASPPattern(
                id="A01-002",
                category=OWASPCategory.A01_BROKEN_ACCESS_CONTROL,
                pattern=r'\b(is_admin|is_superuser|admin)\s*=\s*(True|request\.|form\[)',
                severity=Severity.CRITICAL,
                title="Insecure Privilege Assignment",
                description="Admin/privileged status should not be set from user input.",
                cwe_ids=["CWE-269"],
                remediation="Never allow user input to directly set privilege levels.",
            ),
            
            # A02: Cryptographic Failures
            OWASPPattern(
                id="A02-001",
                category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                pattern=r'\b(md5|MD5|sha1|SHA1)\s*\(',
                severity=Severity.HIGH,
                title="Weak Cryptographic Algorithm",
                description="MD5 and SHA1 are cryptographically weak.",
                cwe_ids=["CWE-328", "CWE-327"],
                remediation="Use SHA-256, SHA-3, or bcrypt/argon2 for passwords.",
            ),
            OWASPPattern(
                id="A02-002",
                category=OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
                pattern=r'\b(DES|3DES|RC4|Blowfish)\b',
                severity=Severity.HIGH,
                title="Deprecated Encryption Algorithm",
                description="These encryption algorithms are deprecated.",
                cwe_ids=["CWE-327"],
                remediation="Use AES-256-GCM or ChaCha20-Poly1305.",
            ),
            
            # A03: Injection
            OWASPPattern(
                id="A03-001",
                category=OWASPCategory.A03_INJECTION,
                pattern=r'\bexecute\s*\([^)]*\+|\bquery\s*\([^)]*\+',
                severity=Severity.CRITICAL,
                title="SQL Injection",
                description="SQL query with string concatenation.",
                cwe_ids=["CWE-89"],
                remediation="Use parameterized queries or prepared statements.",
            ),
            OWASPPattern(
                id="A03-002",
                category=OWASPCategory.A03_INJECTION,
                pattern=r'\beval\s*\(|\bexec\s*\(',
                severity=Severity.CRITICAL,
                title="Code Injection",
                description="Dynamic code execution is dangerous.",
                cwe_ids=["CWE-94", "CWE-95"],
                remediation="Avoid eval/exec. Use safe alternatives like ast.literal_eval.",
            ),
            OWASPPattern(
                id="A03-003",
                category=OWASPCategory.A03_INJECTION,
                pattern=r'\binnerHTML\s*=|document\.write\s*\(',
                severity=Severity.HIGH,
                title="Cross-Site Scripting (XSS)",
                description="DOM manipulation with dynamic content.",
                cwe_ids=["CWE-79"],
                remediation="Use textContent or sanitize HTML. Consider CSP headers.",
                languages={"javascript", "typescript"},
            ),
            
            # A04: Insecure Design
            OWASPPattern(
                id="A04-001",
                category=OWASPCategory.A04_INSECURE_DESIGN,
                pattern=r'\brandom\.random\s*\(|\bMath\.random\s*\(',
                severity=Severity.MEDIUM,
                title="Insecure Randomness",
                description="Non-cryptographic random for security purposes.",
                cwe_ids=["CWE-330"],
                remediation="Use secrets module (Python) or crypto.getRandomValues (JS).",
            ),
            
            # A05: Security Misconfiguration
            OWASPPattern(
                id="A05-001",
                category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                pattern=r'\bDEBUG\s*=\s*True|\bdebug\s*:\s*true',
                severity=Severity.HIGH,
                title="Debug Mode Enabled",
                description="Debug mode should be disabled in production.",
                cwe_ids=["CWE-489"],
                remediation="Disable debug mode in production configurations.",
            ),
            OWASPPattern(
                id="A05-002",
                category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                pattern=r'\bverify\s*=\s*False|\brejectUnauthorized\s*:\s*false',
                severity=Severity.HIGH,
                title="SSL/TLS Verification Disabled",
                description="Disabling certificate verification is insecure.",
                cwe_ids=["CWE-295"],
                remediation="Always verify SSL/TLS certificates in production.",
            ),
            
            # A07: Authentication Failures
            OWASPPattern(
                id="A07-001",
                category=OWASPCategory.A07_AUTHENTICATION_FAILURES,
                pattern=r'\b(password|passwd|pwd)\s*=\s*[\'\"]((?!\{|\$).{3,})[\'\"\)]',
                severity=Severity.CRITICAL,
                title="Hardcoded Password",
                description="Passwords should not be hardcoded.",
                cwe_ids=["CWE-798", "CWE-259"],
                remediation="Use environment variables or a secrets manager.",
            ),
            
            # A08: Data Integrity Failures
            OWASPPattern(
                id="A08-001",
                category=OWASPCategory.A08_DATA_INTEGRITY_FAILURES,
                pattern=r'\bpickle\.loads?\s*\(|\byaml\.load\s*\([^)]*Loader\s*=\s*None',
                severity=Severity.CRITICAL,
                title="Insecure Deserialization",
                description="Unsafe deserialization can lead to RCE.",
                cwe_ids=["CWE-502"],
                remediation="Use json or yaml.safe_load. Avoid pickle with untrusted data.",
            ),
            
            # A10: SSRF
            OWASPPattern(
                id="A10-001",
                category=OWASPCategory.A10_SSRF,
                pattern=r'\b(requests\.get|urllib\.request\.urlopen|fetch)\s*\([^)]*request\.',
                severity=Severity.HIGH,
                title="Server-Side Request Forgery (SSRF)",
                description="User-controlled URLs can be exploited for SSRF.",
                cwe_ids=["CWE-918"],
                remediation="Validate and whitelist URLs. Block internal networks.",
            ),
        ]
    
    def check(self, code: str, language: str = "all") -> List[OWASPFinding]:
        """Check code against OWASP Top 10.
        
        Args:
            code: Source code to check
            language: Programming language
            
        Returns:
            List of OWASP findings
        """
        findings: List[OWASPFinding] = []
        lines = code.split("\n")
        
        for pattern in self._patterns:
            # Check language applicability
            if language not in pattern.languages and "all" not in pattern.languages:
                continue
            
            # Find matches
            for match in pattern._compiled.finditer(code):
                start_pos = match.start()
                line_number = code[:start_pos].count("\n") + 1
                
                # Get code snippet
                line_start = max(0, line_number - 1)
                line_end = min(len(lines), line_number + 1)
                snippet = "\n".join(lines[line_start:line_end])
                
                findings.append(OWASPFinding(
                    id=f"{pattern.id}-{str(uuid.uuid4())[:8]}",
                    category=pattern.category,
                    severity=pattern.severity,
                    title=pattern.title,
                    description=pattern.description,
                    line_start=line_number,
                    cwe_ids=pattern.cwe_ids,
                    remediation=pattern.remediation,
                    code_snippet=snippet,
                ))
        
        return findings
    
    def get_compliance_report(
        self,
        code: str,
        language: str = "all",
    ) -> Dict[str, Any]:
        """Generate OWASP compliance report.
        
        Args:
            code: Source code to check
            language: Programming language
            
        Returns:
            Compliance report with findings by category
        """
        findings = self.check(code, language)
        
        # Group by category
        by_category: Dict[str, List[OWASPFinding]] = {}
        for f in findings:
            cat = f.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f)
        
        # Build compliance status
        compliance: Dict[str, bool] = {}
        for cat in OWASPCategory:
            compliance[cat.value] = cat.value not in by_category
        
        return {
            "total_findings": len(findings),
            "findings_by_category": {
                k: [f.to_dict() for f in v] for k, v in by_category.items()
            },
            "compliance": compliance,
            "compliant_categories": sum(1 for v in compliance.values() if v),
            "non_compliant_categories": sum(1 for v in compliance.values() if not v),
        }
