"""Static code analysis for security vulnerabilities.

World-Class Standards:
- OWASP vulnerability detection
- SQL injection detection
- XSS vulnerability detection
- Path traversal detection
- Command injection detection
"""
import re
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from ..models import SecurityFinding, ThreatType, Severity


@dataclass
class VulnerabilityPattern:
    """Definition of a code vulnerability pattern."""
    name: str
    pattern: str
    severity: Severity
    message: str
    cwe_id: str
    remediation: str
    languages: List[str]  # Applicable languages


class CodeScanner:
    """Static code analysis for security vulnerabilities.
    
    Detects common security issues including:
    - SQL Injection (CWE-89)
    - Cross-Site Scripting (CWE-79)
    - Path Traversal (CWE-22)
    - Command Injection (CWE-78)
    - Insecure Deserialization (CWE-502)
    """
    
    VULNERABILITY_PATTERNS: Dict[str, VulnerabilityPattern] = {
        # SQL Injection
        "sql_injection_concat": VulnerabilityPattern(
            name="sql_injection_concat",
            pattern=r"(?i)(execute|exec|query|cursor\.execute)\s*\(\s*['\"].*[+%]|f['\"].*\{.*\}.*SELECT|INSERT|UPDATE|DELETE",
            severity=Severity.CRITICAL,
            message="Potential SQL injection via string concatenation",
            cwe_id="CWE-89",
            remediation="Use parameterized queries or ORM",
            languages=["python", "javascript", "typescript"],
        ),
        "sql_injection_format": VulnerabilityPattern(
            name="sql_injection_format",
            pattern=r"(?i)\.format\s*\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)",
            severity=Severity.CRITICAL,
            message="Potential SQL injection via string formatting",
            cwe_id="CWE-89",
            remediation="Use parameterized queries or ORM",
            languages=["python"],
        ),
        
        # XSS Vulnerabilities
        "xss_innerhtml": VulnerabilityPattern(
            name="xss_innerhtml",
            pattern=r"(?i)\.innerHTML\s*=\s*[^'\"]*(\+|\$\{|\%s)",
            severity=Severity.HIGH,
            message="Potential XSS via innerHTML assignment",
            cwe_id="CWE-79",
            remediation="Use textContent or sanitize HTML input",
            languages=["javascript", "typescript"],
        ),
        "xss_document_write": VulnerabilityPattern(
            name="xss_document_write",
            pattern=r"(?i)document\.write\s*\(",
            severity=Severity.HIGH,
            message="Use of document.write is XSS-prone",
            cwe_id="CWE-79",
            remediation="Use DOM manipulation methods instead",
            languages=["javascript", "typescript"],
        ),
        
        # Path Traversal
        "path_traversal": VulnerabilityPattern(
            name="path_traversal",
            pattern=r"(?i)(open|read_file|readFile|fs\.read)\s*\([^)]*\+\s*[a-zA-Z_]+",
            severity=Severity.HIGH,
            message="Potential path traversal vulnerability",
            cwe_id="CWE-22",
            remediation="Validate and sanitize file paths, use allowlists",
            languages=["python", "javascript", "typescript"],
        ),
        "path_traversal_dots": VulnerabilityPattern(
            name="path_traversal_dots",
            pattern=r"\.\./",
            severity=Severity.MEDIUM,
            message="Relative path traversal pattern detected",
            cwe_id="CWE-22",
            remediation="Validate and normalize file paths",
            languages=["python", "javascript", "typescript"],
        ),
        
        # Command Injection
        "command_injection_shell": VulnerabilityPattern(
            name="command_injection_shell",
            pattern=r"(?i)(subprocess\.(?:call|run|Popen)|os\.system|os\.popen|exec|eval)\s*\([^)]*(?:\+|\$\{|format)",
            severity=Severity.CRITICAL,
            message="Potential command injection vulnerability",
            cwe_id="CWE-78",
            remediation="Use subprocess with shell=False and list arguments",
            languages=["python"],
        ),
        "command_injection_exec": VulnerabilityPattern(
            name="command_injection_exec",
            pattern=r"(?i)child_process\.exec\s*\([^)]*\+",
            severity=Severity.CRITICAL,
            message="Potential command injection via child_process",
            cwe_id="CWE-78",
            remediation="Use execFile with arguments array",
            languages=["javascript", "typescript"],
        ),
        
        # Insecure Deserialization
        "insecure_pickle": VulnerabilityPattern(
            name="insecure_pickle",
            pattern=r"(?i)pickle\.load[s]?\s*\(",
            severity=Severity.HIGH,
            message="Unsafe deserialization with pickle",
            cwe_id="CWE-502",
            remediation="Use safe serialization formats like JSON",
            languages=["python"],
        ),
        "insecure_yaml": VulnerabilityPattern(
            name="insecure_yaml",
            pattern=r"(?i)yaml\.load\s*\([^)]*(?<!Loader\s*=\s*yaml\.SafeLoader)\)",
            severity=Severity.HIGH,
            message="Unsafe YAML loading without SafeLoader",
            cwe_id="CWE-502",
            remediation="Use yaml.safe_load() or specify SafeLoader",
            languages=["python"],
        ),
        
        # Hardcoded Secrets (complement to SecretsScanner)
        "hardcoded_password": VulnerabilityPattern(
            name="hardcoded_password",
            pattern=r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}['\"]",
            severity=Severity.HIGH,
            message="Hardcoded password detected",
            cwe_id="CWE-259",
            remediation="Use environment variables or secure vault",
            languages=["python", "javascript", "typescript"],
        ),
        
        # Insecure Cryptography
        "weak_hash_md5": VulnerabilityPattern(
            name="weak_hash_md5",
            pattern=r"(?i)(?:hashlib\.)?md5\s*\(",
            severity=Severity.MEDIUM,
            message="Use of weak MD5 hash function",
            cwe_id="CWE-327",
            remediation="Use SHA-256 or stronger hash functions",
            languages=["python"],
        ),
        "weak_hash_sha1": VulnerabilityPattern(
            name="weak_hash_sha1",
            pattern=r"(?i)(?:hashlib\.)?sha1\s*\(",
            severity=Severity.MEDIUM,
            message="Use of weak SHA-1 hash function",
            cwe_id="CWE-327",
            remediation="Use SHA-256 or stronger hash functions",
            languages=["python"],
        ),
        
        # Debug/Development Artifacts
        "debug_enabled": VulnerabilityPattern(
            name="debug_enabled",
            pattern=r"(?i)DEBUG\s*=\s*True",
            severity=Severity.MEDIUM,
            message="Debug mode enabled in code",
            cwe_id="CWE-489",
            remediation="Disable debug mode in production",
            languages=["python"],
        ),
    }
    
    def __init__(self):
        """Initialize scanner with compiled patterns."""
        self._compiled: Dict[str, re.Pattern] = {
            name: re.compile(vuln.pattern)
            for name, vuln in self.VULNERABILITY_PATTERNS.items()
        }
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
        }
        return ext_map.get(file_path.suffix.lower())
    
    def scan_text(
        self,
        text: str,
        source: str = "input",
        language: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Scan text for code vulnerabilities.
        
        Args:
            text: Code content to scan
            source: Source identifier
            language: Programming language (auto-detected if None)
            
        Returns:
            List of security findings
        """
        findings = []
        lines = text.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            for name, compiled in self._compiled.items():
                vuln = self.VULNERABILITY_PATTERNS[name]
                
                # Skip if language doesn't match
                if language and language not in vuln.languages:
                    continue
                
                if compiled.search(line):
                    findings.append(SecurityFinding(
                        id=str(uuid.uuid4()),
                        threat_type=ThreatType.CODE_INJECTION,
                        severity=vuln.severity,
                        message=vuln.message,
                        source=source,
                        line_number=line_num,
                        evidence=line.strip()[:100],  # Truncate long lines
                        remediation=vuln.remediation,
                        cwe_id=vuln.cwe_id,
                    ))
        
        return findings
    
    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan a file for code vulnerabilities.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of security findings
        """
        path = Path(file_path)
        
        if not path.exists():
            return []
        
        language = self._detect_language(path)
        if not language:
            return []  # Skip unsupported languages
        
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            return []
        
        return self.scan_text(content, str(path), language)
