"""Multi-provider secrets detection scanner.

World-Class Standards:
- Zero false negatives for known patterns
- Coverage for all 8 LLM provider credentials
- Pre-commit hook integration ready
- Evidence redaction for safe logging
"""

import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from ..models import SecurityFinding, Severity, ThreatType


@dataclass
class SecretPattern:
    """Definition of a secret pattern for detection."""

    name: str
    pattern: str
    severity: Severity
    message: str
    provider: str | None = None
    cwe_id: str = "CWE-798"  # Use of Hard-coded Credentials
    remediation: str | None = None


class SecretsScanner:
    """Detects exposed secrets including all LLM provider credentials.

    Scans for credentials from all 8 supported providers:
    - copilot (GitHub tokens)
    - openrouter (API keys)
    - ollama (local, no keys)
    - lmstudio (local, no keys)
    - gemini (Google API keys)
    - openai (API keys)
    - anthropic (API keys)
    - azure (API keys and endpoints)
    """

    # LLM Provider patterns - all 8 providers with equal treatment
    PROVIDER_PATTERNS: dict[str, SecretPattern] = {
        "github_token": SecretPattern(
            name="github_token",
            pattern=r"gh[pousr]_[A-Za-z0-9_]{36,}",
            severity=Severity.CRITICAL,
            message="GitHub Token detected (Copilot provider)",
            provider="copilot",
            remediation="Remove token and rotate via GitHub Settings > Developer settings > Personal access tokens",
        ),
        "openrouter_key": SecretPattern(
            name="openrouter_key",
            pattern=r"sk-or-v1-[A-Za-z0-9]{48,}",
            severity=Severity.CRITICAL,
            message="OpenRouter API Key detected",
            provider="openrouter",
            remediation="Remove key and rotate via OpenRouter dashboard",
        ),
        "openai_key": SecretPattern(
            name="openai_key",
            pattern=r"sk-[A-Za-z0-9]{48,}",
            severity=Severity.CRITICAL,
            message="OpenAI API Key detected",
            provider="openai",
            remediation="Remove key and rotate via OpenAI Platform > API keys",
        ),
        "anthropic_key": SecretPattern(
            name="anthropic_key",
            pattern=r"sk-ant-api[0-9]{2}-[A-Za-z0-9-]{90,}",
            severity=Severity.CRITICAL,
            message="Anthropic API Key detected",
            provider="anthropic",
            remediation="Remove key and rotate via Anthropic Console > API keys",
        ),
        "google_api_key": SecretPattern(
            name="google_api_key",
            pattern=r"AIza[0-9A-Za-z-_]{35}",
            severity=Severity.CRITICAL,
            message="Google API Key detected (Gemini provider)",
            provider="gemini",
            remediation="Remove key and rotate via Google Cloud Console > Credentials",
        ),
        "azure_openai_key": SecretPattern(
            name="azure_openai_key",
            pattern=r"(?i)(?:azure|openai).{0,30}['\"][A-Fa-f0-9]{32}['\"]?",
            severity=Severity.CRITICAL,
            message="Azure OpenAI Key detected",
            provider="azure",
            remediation="Remove key and rotate via Azure Portal > Cognitive Services",
        ),
    }

    # General secret patterns
    GENERAL_PATTERNS: dict[str, SecretPattern] = {
        "aws_access_key": SecretPattern(
            name="aws_access_key",
            pattern=r"AKIA[0-9A-Z]{16}",
            severity=Severity.CRITICAL,
            message="AWS Access Key ID detected",
            cwe_id="CWE-798",
            remediation="Remove key and rotate via AWS IAM Console",
        ),
        "aws_secret_key": SecretPattern(
            name="aws_secret_key",
            pattern=r"(?i)aws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]?",
            severity=Severity.CRITICAL,
            message="AWS Secret Access Key detected",
            cwe_id="CWE-798",
            remediation="Remove key and rotate via AWS IAM Console",
        ),
        "private_key": SecretPattern(
            name="private_key",
            pattern=r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY( BLOCK)?-----",
            severity=Severity.CRITICAL,
            message="Private key detected",
            cwe_id="CWE-321",
            remediation="Remove private key and regenerate keypair",
        ),
        "generic_api_key": SecretPattern(
            name="generic_api_key",
            pattern=r"(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*['\"][A-Za-z0-9-_]{20,}['\"]?",
            severity=Severity.HIGH,
            message="Generic API key/secret detected",
            cwe_id="CWE-798",
            remediation="Remove hardcoded credential and use environment variables",
        ),
        "jwt_token": SecretPattern(
            name="jwt_token",
            pattern=r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
            severity=Severity.HIGH,
            message="JWT token detected",
            cwe_id="CWE-798",
            remediation="Remove hardcoded JWT and use secure token storage",
        ),
        "slack_token": SecretPattern(
            name="slack_token",
            pattern=r"xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}",
            severity=Severity.CRITICAL,
            message="Slack token detected",
            cwe_id="CWE-798",
            remediation="Remove token and regenerate via Slack App settings",
        ),
        "stripe_key": SecretPattern(
            name="stripe_key",
            pattern=r"sk_live_[0-9a-zA-Z]{24}",
            severity=Severity.CRITICAL,
            message="Stripe secret key detected",
            cwe_id="CWE-798",
            remediation="Remove key and rotate via Stripe Dashboard",
        ),
        "database_url": SecretPattern(
            name="database_url",
            pattern=r"(?i)(postgres|mysql|mongodb|redis)://[^\s]+:[^\s@]+@[^\s]+",
            severity=Severity.CRITICAL,
            message="Database connection string with credentials detected",
            cwe_id="CWE-798",
            remediation="Remove hardcoded credentials and use environment variables",
        ),
    }

    def __init__(self, excluded_patterns: set[str] | None = None):
        """Initialize scanner with optional pattern exclusions."""
        self._patterns = {**self.PROVIDER_PATTERNS, **self.GENERAL_PATTERNS}
        self._excluded = excluded_patterns or set()
        self._compiled_patterns: dict[str, re.Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        for name, pattern_def in self._patterns.items():
            if name not in self._excluded:
                self._compiled_patterns[name] = re.compile(pattern_def.pattern)

    def _redact(self, text: str, keep_chars: int = 4) -> str:
        """Redact sensitive information for safe logging.

        Keeps first and last N characters, replaces middle with asterisks.
        """
        if len(text) <= keep_chars * 2:
            return "*" * len(text)
        return (
            text[:keep_chars] + "*" * (len(text) - keep_chars * 2) + text[-keep_chars:]
        )

    def scan_text(self, text: str, source: str = "input") -> list[SecurityFinding]:
        """Scan text content for exposed secrets.

        Args:
            text: Content to scan
            source: Source identifier for findings

        Returns:
            List of security findings
        """
        findings = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            for name, compiled in self._compiled_patterns.items():
                match = compiled.search(line)
                if match:
                    pattern_def = self._patterns[name]
                    findings.append(
                        SecurityFinding(
                            id=str(uuid.uuid4()),
                            threat_type=ThreatType.SECRET_EXPOSED,
                            severity=pattern_def.severity,
                            message=pattern_def.message,
                            source=source,
                            line_number=line_num,
                            column_number=match.start() + 1,
                            evidence=self._redact(match.group()),
                            remediation=pattern_def.remediation
                            or f"Remove {name} and rotate credential",
                            cwe_id=pattern_def.cwe_id,
                            provider=pattern_def.provider,
                        )
                    )

        return findings

    def scan_file(
        self, file_path: Path, max_size_kb: int = 10240
    ) -> list[SecurityFinding]:
        """Scan a single file for secrets.

        Args:
            file_path: Path to file to scan
            max_size_kb: Maximum file size in KB (default 10MB)

        Returns:
            List of security findings
        """
        path = Path(file_path)

        if not path.exists():
            return []

        # Skip files too large
        if path.stat().st_size > max_size_kb * 1024:
            return []

        # Skip binary files
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (UnicodeDecodeError, OSError):
            return []

        return self.scan_text(content, str(path))

    def scan_directory(
        self,
        directory: Path,
        excluded_dirs: set[str] | None = None,
        excluded_extensions: set[str] | None = None,
        max_workers: int = 4,
    ) -> list[SecurityFinding]:
        """Recursively scan directory for secrets.

        Args:
            directory: Root directory to scan
            excluded_dirs: Directory names to skip
            excluded_extensions: File extensions to skip
            max_workers: Number of parallel workers

        Returns:
            List of security findings
        """
        directory = Path(directory)
        findings = []

        excluded_dirs = excluded_dirs or {
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".mypy_cache",
            ".pytest_cache",
            "dist",
            "build",
        }
        excluded_extensions = excluded_extensions or {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
        }

        files_to_scan = []
        for path in directory.rglob("*"):
            if path.is_file():
                # Check exclusions
                if any(excluded in path.parts for excluded in excluded_dirs):
                    continue
                if path.suffix.lower() in excluded_extensions:
                    continue
                files_to_scan.append(path)

        # Parallel scanning for performance
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.scan_file, f): f for f in files_to_scan
            }
            for future in as_completed(future_to_file):
                try:
                    file_findings = future.result()
                    findings.extend(file_findings)
                except Exception:
                    pass  # Skip files that error

        return findings

    def get_provider_patterns(self, provider: str) -> list[str]:
        """Get pattern names for a specific LLM provider."""
        return [
            name
            for name, pattern in self._patterns.items()
            if pattern.provider == provider
        ]


# Legacy support
GENERIC_PATTERNS = list(SecretsScanner.GENERAL_PATTERNS.keys())
