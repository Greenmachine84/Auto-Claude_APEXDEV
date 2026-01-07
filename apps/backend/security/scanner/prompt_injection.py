"""Prompt injection defense with multi-layer protection.

World-Class Standards:
- OWASP LLM01 prompt injection mitigation
- Multi-layer defense strategy
- Input sanitization and validation
- Attack pattern detection with high accuracy
"""
import re
import uuid
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass

from ..models import SecurityFinding, ThreatType, Severity, ValidationResult


@dataclass
class InjectionPattern:
    """Pattern definition for injection detection."""
    pattern: str
    description: str
    severity: Severity
    category: str  # instruction_override, role_hijack, delimiter_escape, etc.


class PromptInjectionGuard:
    """Multi-layer defense against prompt injection attacks.
    
    Implements defense strategies from:
    - OWASP Top 10 for LLM Applications
    - Anthropic prompt injection research
    - Microsoft Copilot spotlighting
    """
    
    # Comprehensive injection patterns
    DETECTION_PATTERNS: List[InjectionPattern] = [
        # Instruction override attempts
        InjectionPattern(
            pattern=r"(?i)ignore\s+(all\s+)?previous\s+instructions?",
            description="Instruction override attempt",
            severity=Severity.HIGH,
            category="instruction_override",
        ),
        InjectionPattern(
            pattern=r"(?i)disregard\s+(all\s+)?prior\s+(instructions?|context)",
            description="Instruction disregard attempt",
            severity=Severity.HIGH,
            category="instruction_override",
        ),
        InjectionPattern(
            pattern=r"(?i)forget\s+(everything|all)\s+(above|before)",
            description="Context reset attempt",
            severity=Severity.HIGH,
            category="instruction_override",
        ),
        
        # Role hijacking
        InjectionPattern(
            pattern=r"(?i)you\s+are\s+now\s+(a\s+)?different",
            description="Role hijacking attempt",
            severity=Severity.HIGH,
            category="role_hijack",
        ),
        InjectionPattern(
            pattern=r"(?i)pretend\s+(to\s+be|you\'?re)\s+(a\s+)?(different|another)",
            description="Role pretense attempt",
            severity=Severity.HIGH,
            category="role_hijack",
        ),
        InjectionPattern(
            pattern=r"(?i)act\s+as\s+(if\s+)?(you\'?re|a)\s+",
            description="Role acting attempt",
            severity=Severity.MEDIUM,
            category="role_hijack",
        ),
        
        # System prompt extraction
        InjectionPattern(
            pattern=r"(?i)(show|reveal|print|output|display)\s+(me\s+)?(your\s+)?(system\s+)?prompt",
            description="System prompt extraction attempt",
            severity=Severity.HIGH,
            category="prompt_extraction",
        ),
        InjectionPattern(
            pattern=r"(?i)what\s+(is|are)\s+your\s+(system\s+)?(instructions?|rules?|constraints?)",
            description="Instruction extraction attempt",
            severity=Severity.MEDIUM,
            category="prompt_extraction",
        ),
        
        # Delimiter escape attempts
        InjectionPattern(
            pattern=r"\]\]\]|\>\>\>|\}\}\}|\-\-\-\s*END|<\/?system>",
            description="Delimiter escape attempt",
            severity=Severity.HIGH,
            category="delimiter_escape",
        ),
        InjectionPattern(
            pattern=r"```(system|assistant|user)",
            description="Markdown role injection",
            severity=Severity.MEDIUM,
            category="delimiter_escape",
        ),
        
        # Jailbreak attempts
        InjectionPattern(
            pattern=r"(?i)(jailbreak|dan\s+mode|dev\s+mode|developer\s+mode)",
            description="Jailbreak attempt",
            severity=Severity.CRITICAL,
            category="jailbreak",
        ),
        InjectionPattern(
            pattern=r"(?i)enable\s+(unrestricted|uncensored|unlimited)\s+mode",
            description="Unrestricted mode attempt",
            severity=Severity.CRITICAL,
            category="jailbreak",
        ),
        
        # Encoded payloads
        InjectionPattern(
            pattern=r"(?i)(base64|rot13|hex)\s*decode",
            description="Encoded payload attempt",
            severity=Severity.MEDIUM,
            category="encoding",
        ),
        InjectionPattern(
            pattern=r"\\x[0-9A-Fa-f]{2}",
            description="Hex-encoded characters detected",
            severity=Severity.LOW,
            category="encoding",
        ),
        
        # Command injection via LLM
        InjectionPattern(
            pattern=r"(?i)execute\s+(this\s+)?command|run\s+(this\s+)?script",
            description="Command execution request",
            severity=Severity.HIGH,
            category="command_injection",
        ),
    ]
    
    # Compiled patterns for performance
    _compiled_patterns: List[Tuple[re.Pattern, InjectionPattern]] = []
    
    def __init__(self):
        """Initialize guard with compiled patterns."""
        self._compiled_patterns = [
            (re.compile(p.pattern), p) for p in self.DETECTION_PATTERNS
        ]
    
    def check(self, input_text: str) -> ValidationResult:
        """Check input for injection attempts.
        
        Args:
            input_text: User input to validate
            
        Returns:
            ValidationResult with findings
        """
        findings = []
        
        for compiled, pattern_def in self._compiled_patterns:
            if compiled.search(input_text):
                findings.append(SecurityFinding(
                    id=str(uuid.uuid4()),
                    threat_type=ThreatType.PROMPT_INJECTION,
                    severity=pattern_def.severity,
                    message=pattern_def.description,
                    source="user_input",
                    evidence=pattern_def.pattern,
                    remediation="Sanitize input and use delimiters",
                ))
        
        is_valid = len(findings) == 0 or all(
            f.severity in [Severity.LOW, Severity.MEDIUM] for f in findings
        )
        
        return ValidationResult(
            valid=is_valid,
            errors=[f.message for f in findings if f.severity in [Severity.HIGH, Severity.CRITICAL]],
            warnings=[f.message for f in findings if f.severity in [Severity.LOW, Severity.MEDIUM]],
            findings=findings,
        )
    
    def sanitize(self, input_text: str) -> str:
        """Sanitize input by escaping potential injection patterns.
        
        Args:
            input_text: Raw user input
            
        Returns:
            Sanitized input safe for LLM processing
        """
        sanitized = input_text
        
        # Escape common delimiter characters
        escape_chars = {
            "]": "\\]",
            ">": "\\>",
            "}": "\\}",
            "<": "\\<",
            "[": "\\[",
            "{": "\\{",
        }
        for char, escaped in escape_chars.items():
            if char * 3 in sanitized:  # Only escape triple delimiters
                sanitized = sanitized.replace(char * 3, escaped * 3)
        
        return sanitized
    
    def wrap_user_input(self, input_text: str, source: str = "user") -> str:
        """Wrap user input with spotlighting markers.
        
        Microsoft spotlighting technique reduces injection success from >50% to <2%.
        
        Args:
            input_text: User-provided content
            source: Source identifier
            
        Returns:
            Marked input for LLM processing
        """
        marker = f"[{source.upper()}_INPUT]"
        return f"{marker}\n{input_text}\n[END_{source.upper()}_INPUT]"
    
    def validate_output(self, output: str, canary_tokens: Optional[Set[str]] = None) -> ValidationResult:
        """Validate LLM output for prompt leakage.
        
        Args:
            output: LLM-generated output
            canary_tokens: Set of tokens that should never appear in output
            
        Returns:
            ValidationResult indicating if output is safe
        """
        errors = []
        
        # Check for canary token leakage
        if canary_tokens:
            for token in canary_tokens:
                if token in output:
                    errors.append(f"Canary token leakage detected: {token[:8]}...")
        
        # Check for system prompt patterns in output
        system_patterns = [
            r"(?i)system\s*prompt\s*:\s*",
            r"(?i)my\s+instructions\s+are\s*:\s*",
            r"(?i)i\s+was\s+told\s+to\s*:\s*",
        ]
        for pattern in system_patterns:
            if re.search(pattern, output):
                errors.append("Potential system prompt leakage detected")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )


class PromptInjectionScanner:
    """Simplified scanner interface for prompt injection detection.
    
    Provides backward-compatible API for existing code.
    """
    
    PATTERNS = [
        (r"ignore previous instructions", "Instruction override attempt"),
        (r"system prompt", "System prompt leakage attempt"),
        (r"you are not", "Role hijacking attempt"),
        (r"jailbreak", "Jailbreak attempt"),
        (r"pretend to be", "Role pretense attempt"),
        (r"act as if", "Role acting attempt"),
        (r"\]\]\]", "Delimiter escape attempt"),
    ]
    
    def scan(self, text: str) -> List[SecurityFinding]:
        """Scan text for injection attempts.
        
        Args:
            text: Input text to scan
            
        Returns:
            List of security findings
        """
        findings = []
        for pattern, desc in self.PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(SecurityFinding(
                    id=str(uuid.uuid4()),
                    threat_type=ThreatType.PROMPT_INJECTION,
                    severity=Severity.HIGH,
                    message=desc,
                    source="input",
                    evidence=pattern,
                    remediation="Sanitize input and use delimiters",
                ))
        return findings
