"""Severity classifier for code review findings.

World-Class Standards:
- Consistent severity classification
- Pattern-based detection
- Configurable rules

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import re

from ..types import Severity


@dataclass
class ClassificationResult:
    """Result of severity classification."""
    severity: Severity
    confidence: float  # 0.0 - 1.0
    matched_patterns: List[str] = field(default_factory=list)
    reasoning: str = ""


class SeverityClassifier:
    """Classifies finding severity based on content and category.
    
    Uses pattern matching and heuristics to determine severity.
    
    Severity Levels:
        - CRITICAL: Security vulnerabilities, data loss risks
        - HIGH: Bugs, logic errors, major issues
        - MEDIUM: Code quality issues, moderate concerns
        - LOW: Style, documentation, minor issues
        - INFO: Suggestions, informational only
    """
    
    # Patterns for critical issues
    CRITICAL_PATTERNS: Set[str] = {
        r"sql\s*injection",
        r"command\s*injection",
        r"xss|cross[\-\s]*site\s*scripting",
        r"remote\s*code\s*execution",
        r"authentication\s*bypass",
        r"privilege\s*escalation",
        r"secret|password|api[\-\s]*key\s*exposed",
        r"hardcoded\s*(password|secret|credential)",
        r"path\s*traversal",
        r"xxe|xml\s*external\s*entity",
        r"ssrf|server[\-\s]*side\s*request\s*forgery",
        r"deserialization",
        r"buffer\s*overflow",
    }
    
    # Patterns for high severity
    HIGH_PATTERNS: Set[str] = {
        r"null\s*pointer|nullptr|nullreference",
        r"race\s*condition",
        r"deadlock",
        r"memory\s*leak",
        r"infinite\s*loop",
        r"unhandled\s*exception",
        r"data\s*loss",
        r"incorrect\s*logic",
        r"broken\s*functionality",
        r"resource\s*leak",
        r"unchecked\s*(input|user\s*input)",
        r"insecure\s*(random|crypto)",
    }
    
    # Patterns for medium severity
    MEDIUM_PATTERNS: Set[str] = {
        r"code\s*smell",
        r"complexity",
        r"duplicate\s*code",
        r"long\s*method|long\s*function",
        r"magic\s*number",
        r"deprecated",
        r"inefficient",
        r"performance\s*issue",
        r"missing\s*error\s*handling",
        r"incomplete\s*implementation",
    }
    
    # Patterns for low severity
    LOW_PATTERNS: Set[str] = {
        r"naming\s*convention",
        r"formatting",
        r"whitespace",
        r"indentation",
        r"missing\s*docstring|missing\s*documentation",
        r"todo|fixme",
        r"unused\s*(variable|import|parameter)",
        r"spelling",
        r"typo",
    }
    
    # Category mappings to default severity
    CATEGORY_SEVERITY: Dict[str, Severity] = {
        "security": Severity.CRITICAL,
        "vulnerability": Severity.CRITICAL,
        "bug": Severity.HIGH,
        "error": Severity.HIGH,
        "logic": Severity.HIGH,
        "performance": Severity.MEDIUM,
        "quality": Severity.MEDIUM,
        "maintainability": Severity.MEDIUM,
        "style": Severity.LOW,
        "documentation": Severity.LOW,
        "formatting": Severity.LOW,
        "suggestion": Severity.INFO,
        "improvement": Severity.INFO,
        "info": Severity.INFO,
    }
    
    def __init__(self):
        """Initialize the classifier with compiled patterns."""
        self._compiled_critical = self._compile_patterns(self.CRITICAL_PATTERNS)
        self._compiled_high = self._compile_patterns(self.HIGH_PATTERNS)
        self._compiled_medium = self._compile_patterns(self.MEDIUM_PATTERNS)
        self._compiled_low = self._compile_patterns(self.LOW_PATTERNS)
    
    def _compile_patterns(self, patterns: Set[str]) -> List[re.Pattern]:
        """Compile pattern set to regex objects."""
        return [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def classify(
        self,
        message: str,
        category: str = "",
    ) -> Severity:
        """Classify severity based on message and category.
        
        Args:
            message: The finding message
            category: Optional category hint
            
        Returns:
            Classified severity level
        """
        result = self.classify_detailed(message, category)
        return result.severity
    
    def classify_detailed(
        self,
        message: str,
        category: str = "",
    ) -> ClassificationResult:
        """Classify with detailed results.
        
        Args:
            message: The finding message
            category: Optional category hint
            
        Returns:
            Detailed classification result
        """
        text = f"{message} {category}".lower()
        matched_patterns: List[str] = []
        
        # Check critical patterns
        for pattern in self._compiled_critical:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)
        if matched_patterns:
            return ClassificationResult(
                severity=Severity.CRITICAL,
                confidence=0.95,
                matched_patterns=matched_patterns,
                reasoning="Matched critical security patterns",
            )
        
        # Check high patterns
        for pattern in self._compiled_high:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)
        if matched_patterns:
            return ClassificationResult(
                severity=Severity.HIGH,
                confidence=0.9,
                matched_patterns=matched_patterns,
                reasoning="Matched high severity patterns",
            )
        
        # Check medium patterns
        for pattern in self._compiled_medium:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)
        if matched_patterns:
            return ClassificationResult(
                severity=Severity.MEDIUM,
                confidence=0.85,
                matched_patterns=matched_patterns,
                reasoning="Matched medium severity patterns",
            )
        
        # Check low patterns
        for pattern in self._compiled_low:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)
        if matched_patterns:
            return ClassificationResult(
                severity=Severity.LOW,
                confidence=0.8,
                matched_patterns=matched_patterns,
                reasoning="Matched low severity patterns",
            )
        
        # Fall back to category-based classification
        category_lower = category.lower()
        for cat, severity in self.CATEGORY_SEVERITY.items():
            if cat in category_lower:
                return ClassificationResult(
                    severity=severity,
                    confidence=0.7,
                    matched_patterns=[],
                    reasoning=f"Classified by category: {cat}",
                )
        
        # Default to INFO
        return ClassificationResult(
            severity=Severity.INFO,
            confidence=0.5,
            matched_patterns=[],
            reasoning="No specific patterns matched, defaulting to INFO",
        )
