"""Input validation for LLM requests.

World-Class Standards:
- Content length limits
- Character encoding validation
- Prompt injection pre-screening
- Rate limiting support
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ..models import SecurityFinding, Severity, ThreatType, ValidationResult
from ..scanner.prompt_injection import PromptInjectionGuard
from ..scanner.sanitizer import InputSanitizer


@dataclass
class InputConstraints:
    """Constraints for input validation."""

    max_length: int = 100_000  # 100KB default
    max_tokens: int | None = None  # Token limit if applicable
    allowed_languages: list[str] | None = None  # Language codes
    block_code: bool = False  # Block code blocks
    block_urls: bool = False  # Block URLs
    block_emails: bool = False  # Block email addresses
    require_ascii: bool = False  # Only ASCII characters
    custom_blocked_patterns: list[str] = field(default_factory=list)


class InputValidator:
    """Validates and sanitizes LLM input.

    Provides multi-layer input validation:
    1. Length and encoding checks
    2. Content policy enforcement
    3. Prompt injection detection
    4. Custom constraint validation

    Example:
        validator = InputValidator()
        result = validator.validate(user_input)

        if result.valid:
            # Process input
            pass
        else:
            # Handle validation errors
            for error in result.errors:
                print(error)
    """

    def __init__(
        self,
        constraints: InputConstraints | None = None,
        sanitizer: InputSanitizer | None = None,
        injection_guard: PromptInjectionGuard | None = None,
    ):
        """Initialize input validator.

        Args:
            constraints: Validation constraints
            sanitizer: Input sanitizer instance
            injection_guard: Prompt injection guard
        """
        self._constraints = constraints or InputConstraints()
        self._sanitizer = sanitizer or InputSanitizer()
        self._injection_guard = injection_guard or PromptInjectionGuard()
        self._compiled_patterns: list[re.Pattern] = []

        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile custom blocked patterns."""
        for pattern in self._constraints.custom_blocked_patterns:
            try:
                self._compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                pass

    def validate(
        self,
        input_text: str,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate input text.

        Args:
            input_text: User input to validate
            context: Optional validation context

        Returns:
            ValidationResult with status and findings
        """
        errors = []
        warnings = []
        findings = []

        # 1. Length check
        if len(input_text) > self._constraints.max_length:
            errors.append(
                f"Input exceeds maximum length of {self._constraints.max_length} characters"
            )
            findings.append(
                SecurityFinding(
                    id="length_exceeded",
                    threat_type=ThreatType.MALFORMED_INPUT,
                    severity=Severity.MEDIUM,
                    message="Input length exceeds maximum",
                    source="input_validator",
                )
            )

        # 2. Encoding check
        if self._constraints.require_ascii:
            try:
                input_text.encode("ascii")
            except UnicodeEncodeError:
                errors.append("Input contains non-ASCII characters")
                findings.append(
                    SecurityFinding(
                        id="non_ascii",
                        threat_type=ThreatType.MALFORMED_INPUT,
                        severity=Severity.LOW,
                        message="Non-ASCII characters in input",
                        source="input_validator",
                    )
                )

        # 3. Control character check
        control_chars = sum(
            1
            for c in input_text
            if unicodedata.category(c) == "Cc" and c not in "\n\r\t"
        )
        if control_chars > 0:
            warnings.append(f"Input contains {control_chars} control characters")
            findings.append(
                SecurityFinding(
                    id="control_chars",
                    threat_type=ThreatType.MALFORMED_INPUT,
                    severity=Severity.LOW,
                    message=f"Control characters detected: {control_chars}",
                    source="input_validator",
                )
            )

        # 4. Content blocking
        if self._constraints.block_code:
            code_pattern = r"```[\s\S]*?```|`[^`]+`"
            if re.search(code_pattern, input_text):
                errors.append("Code blocks are not allowed")
                findings.append(
                    SecurityFinding(
                        id="code_blocked",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.MEDIUM,
                        message="Code blocks blocked by policy",
                        source="input_validator",
                    )
                )

        if self._constraints.block_urls:
            url_pattern = r"https?://[^\s]+"
            if re.search(url_pattern, input_text):
                errors.append("URLs are not allowed")
                findings.append(
                    SecurityFinding(
                        id="url_blocked",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.MEDIUM,
                        message="URLs blocked by policy",
                        source="input_validator",
                    )
                )

        if self._constraints.block_emails:
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            if re.search(email_pattern, input_text):
                errors.append("Email addresses are not allowed")
                findings.append(
                    SecurityFinding(
                        id="email_blocked",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.MEDIUM,
                        message="Email addresses blocked by policy",
                        source="input_validator",
                    )
                )

        # 5. Custom pattern blocking
        for i, pattern in enumerate(self._compiled_patterns):
            if pattern.search(input_text):
                errors.append(f"Input matches blocked pattern #{i + 1}")
                findings.append(
                    SecurityFinding(
                        id=f"blocked_pattern_{i}",
                        threat_type=ThreatType.POLICY_VIOLATION,
                        severity=Severity.HIGH,
                        message="Blocked pattern detected",
                        source="input_validator",
                    )
                )

        # 6. Prompt injection check
        injection_result = self._injection_guard.check(input_text)
        if not injection_result.valid:
            errors.extend(injection_result.errors)
            warnings.extend(injection_result.warnings)
            findings.extend(injection_result.findings or [])

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            findings=findings,
        )

    def sanitize(self, input_text: str) -> str:
        """Sanitize input text.

        Args:
            input_text: Raw user input

        Returns:
            Sanitized input
        """
        return self._sanitizer.sanitize_for_llm(input_text)

    def validate_and_sanitize(
        self,
        input_text: str,
        context: dict[str, Any] | None = None,
    ) -> tuple:
        """Validate and sanitize input in one call.

        Args:
            input_text: User input
            context: Optional context

        Returns:
            Tuple of (ValidationResult, sanitized_text)
        """
        result = self.validate(input_text, context)

        if result.valid:
            sanitized = self.sanitize(input_text)
        else:
            sanitized = ""

        return result, sanitized

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Uses simple heuristic: ~4 chars per token for English.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token for English
        # More accurate estimation would require tokenizer
        return len(text) // 4

    def wrap_for_llm(self, input_text: str, role: str = "user") -> str:
        """Wrap input with safety markers for LLM processing.

        Uses spotlighting technique to reduce injection success.

        Args:
            input_text: Validated user input
            role: Role identifier

        Returns:
            Wrapped input
        """
        return self._injection_guard.wrap_user_input(input_text, role)

    def update_constraints(self, **kwargs) -> None:
        """Update validation constraints.

        Args:
            **kwargs: Constraint fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self._constraints, key):
                setattr(self._constraints, key, value)

        # Recompile patterns if updated
        if "custom_blocked_patterns" in kwargs:
            self._compile_patterns()
