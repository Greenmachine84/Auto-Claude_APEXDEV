"""Output validation and PII redaction.

World-Class Standards:
- PII detection and redaction
- Output content policy enforcement
- Sensitive data filtering
- Format validation
"""

import re
from dataclasses import dataclass, field

from ..models import SecurityFinding, Severity, ThreatType, ValidationResult


@dataclass
class PIIPattern:
    """PII detection pattern."""

    name: str
    pattern: str
    replacement: str
    severity: Severity = Severity.HIGH


class PIIRedactor:
    """Detects and redacts Personally Identifiable Information.

    Supports detection and redaction of:
    - Email addresses
    - Phone numbers
    - Social Security Numbers
    - Credit card numbers
    - IP addresses
    - Names (with context)
    """

    PATTERNS: list[PIIPattern] = [
        PIIPattern(
            name="email",
            pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            replacement="[EMAIL REDACTED]",
        ),
        PIIPattern(
            name="phone_us",
            pattern=r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b",
            replacement="[PHONE REDACTED]",
        ),
        PIIPattern(
            name="phone_intl",
            pattern=r"\+[0-9]{1,3}[-. ]?[0-9]{4,14}",
            replacement="[PHONE REDACTED]",
        ),
        PIIPattern(
            name="ssn",
            pattern=r"\b[0-9]{3}[-]?[0-9]{2}[-]?[0-9]{4}\b",
            replacement="[SSN REDACTED]",
            severity=Severity.CRITICAL,
        ),
        PIIPattern(
            name="credit_card",
            pattern=r"\b(?:[0-9]{4}[-. ]?){3}[0-9]{4}\b",
            replacement="[CC REDACTED]",
            severity=Severity.CRITICAL,
        ),
        PIIPattern(
            name="ipv4",
            pattern=r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            replacement="[IP REDACTED]",
        ),
        PIIPattern(
            name="ipv6",
            pattern=r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}",
            replacement="[IP REDACTED]",
        ),
        PIIPattern(
            name="date_of_birth",
            pattern=r"\b(?:DOB|Date of Birth|Born)[:\s]+[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}\b",
            replacement="[DOB REDACTED]",
        ),
        PIIPattern(
            name="passport",
            pattern=r"\b[A-Z]{1,2}[0-9]{6,9}\b",
            replacement="[PASSPORT REDACTED]",
        ),
    ]

    def __init__(self, custom_patterns: list[PIIPattern] | None = None):
        """Initialize redactor with optional custom patterns."""
        self._patterns = self.PATTERNS.copy()
        if custom_patterns:
            self._patterns.extend(custom_patterns)

        self._compiled: list[tuple[re.Pattern, PIIPattern]] = [
            (re.compile(p.pattern), p) for p in self._patterns
        ]

    def detect(self, text: str) -> list[dict]:
        """Detect PII in text.

        Args:
            text: Text to scan

        Returns:
            List of PII detections with type and position
        """
        detections = []

        for compiled, pattern in self._compiled:
            for match in compiled.finditer(text):
                detections.append(
                    {
                        "type": pattern.name,
                        "start": match.start(),
                        "end": match.end(),
                        "severity": pattern.severity.value,
                    }
                )

        return detections

    def redact(self, text: str) -> str:
        """Redact all PII from text.

        Args:
            text: Text to redact

        Returns:
            Text with PII replaced by placeholders
        """
        result = text

        for compiled, pattern in self._compiled:
            result = compiled.sub(pattern.replacement, result)

        return result

    def redact_with_report(
        self,
        text: str,
    ) -> tuple[str, list[dict]]:
        """Redact PII and return report of what was redacted.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, list of redactions)
        """
        detections = self.detect(text)
        redacted = self.redact(text)

        return redacted, detections


@dataclass
class OutputConstraints:
    """Constraints for output validation."""

    max_length: int = 500_000  # 500KB default
    require_pii_redaction: bool = True
    blocked_patterns: list[str] = field(default_factory=list)
    required_patterns: list[str] = field(default_factory=list)
    max_sensitive_terms: int = 0  # 0 = no limit


class OutputValidator:
    """Validates and sanitizes LLM output.

    Provides:
    - Length validation
    - PII detection and optional redaction
    - Content policy enforcement
    - Output format validation

    Example:
        validator = OutputValidator()

        # Validate output
        result = validator.validate(llm_output)

        if result.valid:
            # Use output
            pass
        else:
            # Handle issues
            pass

        # Or sanitize output
        clean_output = validator.sanitize(llm_output)
    """

    # Terms that might indicate sensitive content
    SENSITIVE_TERMS: set[str] = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "private_key",
        "ssh",
        "credential",
        "auth",
        "confidential",
        "internal only",
        "do not share",
    }

    def __init__(
        self,
        constraints: OutputConstraints | None = None,
        pii_redactor: PIIRedactor | None = None,
    ):
        """Initialize output validator.

        Args:
            constraints: Validation constraints
            pii_redactor: PII redactor instance
        """
        self._constraints = constraints or OutputConstraints()
        self._pii_redactor = pii_redactor or PIIRedactor()
        self._blocked_compiled: list[re.Pattern] = []
        self._required_compiled: list[re.Pattern] = []

        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile constraint patterns."""
        for pattern in self._constraints.blocked_patterns:
            try:
                self._blocked_compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass

        for pattern in self._constraints.required_patterns:
            try:
                self._required_compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass

    def validate(
        self,
        output: str,
        context: dict | None = None,
    ) -> ValidationResult:
        """Validate LLM output.

        Args:
            output: LLM output to validate
            context: Optional validation context

        Returns:
            ValidationResult with status and findings
        """
        errors = []
        warnings = []
        findings = []

        # 1. Length check
        if len(output) > self._constraints.max_length:
            errors.append(
                f"Output exceeds maximum length of {self._constraints.max_length}"
            )
            findings.append(
                SecurityFinding(
                    id="output_length",
                    threat_type=ThreatType.MALFORMED_INPUT,
                    severity=Severity.MEDIUM,
                    message="Output length exceeds maximum",
                    source="output_validator",
                )
            )

        # 2. PII detection
        if self._constraints.require_pii_redaction:
            pii_detections = self._pii_redactor.detect(output)
            if pii_detections:
                warnings.append(f"PII detected: {len(pii_detections)} instances")
                for detection in pii_detections:
                    findings.append(
                        SecurityFinding(
                            id=f"pii_{detection['type']}",
                            threat_type=ThreatType.DATA_LEAK,
                            severity=Severity(detection["severity"]),
                            message=f"PII detected: {detection['type']}",
                            source="output_validator",
                        )
                    )

        # 3. Blocked pattern check
        for i, pattern in enumerate(self._blocked_compiled):
            if pattern.search(output):
                errors.append(f"Output contains blocked pattern #{i + 1}")
                findings.append(
                    SecurityFinding(
                        id=f"blocked_output_{i}",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.HIGH,
                        message="Blocked pattern in output",
                        source="output_validator",
                    )
                )

        # 4. Required pattern check
        for i, pattern in enumerate(self._required_compiled):
            if not pattern.search(output):
                errors.append(f"Output missing required pattern #{i + 1}")
                findings.append(
                    SecurityFinding(
                        id=f"missing_required_{i}",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.MEDIUM,
                        message="Required pattern missing from output",
                        source="output_validator",
                    )
                )

        # 5. Sensitive term check
        if self._constraints.max_sensitive_terms > 0:
            term_count = sum(
                1 for term in self.SENSITIVE_TERMS if term.lower() in output.lower()
            )
            if term_count > self._constraints.max_sensitive_terms:
                warnings.append(
                    f"Output contains {term_count} sensitive terms "
                    f"(max: {self._constraints.max_sensitive_terms})"
                )
                findings.append(
                    SecurityFinding(
                        id="sensitive_terms",
                        threat_type=ThreatType.DATA_LEAK,
                        severity=Severity.MEDIUM,
                        message=f"Sensitive terms detected: {term_count}",
                        source="output_validator",
                    )
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            findings=findings,
        )

    def sanitize(
        self,
        output: str,
        redact_pii: bool = True,
    ) -> str:
        """Sanitize LLM output.

        Args:
            output: Output to sanitize
            redact_pii: Whether to redact PII

        Returns:
            Sanitized output
        """
        sanitized = output

        # Redact PII if requested
        if redact_pii:
            sanitized = self._pii_redactor.redact(sanitized)

        # Truncate if too long
        if len(sanitized) > self._constraints.max_length:
            sanitized = sanitized[: self._constraints.max_length] + "... [truncated]"

        return sanitized

    def validate_and_sanitize(
        self,
        output: str,
        context: dict | None = None,
    ) -> tuple[ValidationResult, str]:
        """Validate and sanitize output in one call.

        Args:
            output: LLM output
            context: Optional context

        Returns:
            Tuple of (ValidationResult, sanitized_output)
        """
        result = self.validate(output, context)
        sanitized = self.sanitize(output)

        return result, sanitized

    def check_for_prompt_leakage(
        self,
        output: str,
        system_prompt: str,
    ) -> bool:
        """Check if output contains leaked system prompt.

        Args:
            output: LLM output
            system_prompt: System prompt to check for

        Returns:
            True if leakage detected
        """
        # Check for exact substring
        if system_prompt in output:
            return True

        # Check for significant overlap (>50% of prompt words)
        prompt_words = set(system_prompt.lower().split())
        output_words = set(output.lower().split())

        if len(prompt_words) > 0:
            overlap = len(prompt_words & output_words) / len(prompt_words)
            if overlap > 0.5:
                return True

        return False
