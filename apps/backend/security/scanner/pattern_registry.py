"""Detection pattern registry for centralized pattern management.

World-Class Standards:
- Centralized pattern storage
- Pattern versioning support
- Custom pattern registration
- Pattern validation
"""
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from ..models import Severity


@dataclass
class DetectionPattern:
    """A registered detection pattern."""
    id: str
    name: str
    pattern: str
    description: str
    severity: Severity
    category: str  # secrets, injection, vulnerability, etc.
    enabled: bool = True
    version: str = "1.0.0"
    author: str = "system"
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def compile(self) -> re.Pattern:
        """Compile the regex pattern."""
        return re.compile(self.pattern)
    
    def validate(self) -> List[str]:
        """Validate the pattern configuration."""
        errors = []
        
        if not self.id:
            errors.append("Pattern ID is required")
        if not self.name:
            errors.append("Pattern name is required")
        if not self.pattern:
            errors.append("Pattern regex is required")
        
        try:
            re.compile(self.pattern)
        except re.error as e:
            errors.append(f"Invalid regex pattern: {e}")
        
        return errors


class PatternRegistry:
    """Centralized registry for detection patterns.
    
    Supports:
    - Built-in patterns
    - Custom pattern registration
    - Pattern categorization
    - Version tracking
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._patterns: Dict[str, DetectionPattern] = {}
        self._categories: Dict[str, List[str]] = {}  # category -> pattern IDs
        self._compiled: Dict[str, re.Pattern] = {}
    
    def register(
        self,
        pattern: DetectionPattern,
        overwrite: bool = False,
    ) -> bool:
        """Register a new detection pattern.
        
        Args:
            pattern: Pattern to register
            overwrite: Whether to overwrite existing pattern
            
        Returns:
            True if registration successful
        """
        # Validate pattern
        errors = pattern.validate()
        if errors:
            raise ValueError(f"Invalid pattern: {'; '.join(errors)}")
        
        # Check for existing
        if pattern.id in self._patterns and not overwrite:
            return False
        
        # Register
        self._patterns[pattern.id] = pattern
        self._compiled[pattern.id] = pattern.compile()
        
        # Update category index
        if pattern.category not in self._categories:
            self._categories[pattern.category] = []
        if pattern.id not in self._categories[pattern.category]:
            self._categories[pattern.category].append(pattern.id)
        
        return True
    
    def unregister(self, pattern_id: str) -> bool:
        """Remove a pattern from the registry.
        
        Args:
            pattern_id: ID of pattern to remove
            
        Returns:
            True if pattern was removed
        """
        if pattern_id not in self._patterns:
            return False
        
        pattern = self._patterns[pattern_id]
        
        # Remove from category index
        if pattern.category in self._categories:
            self._categories[pattern.category] = [
                pid for pid in self._categories[pattern.category]
                if pid != pattern_id
            ]
        
        # Remove pattern
        del self._patterns[pattern_id]
        del self._compiled[pattern_id]
        
        return True
    
    def get(self, pattern_id: str) -> Optional[DetectionPattern]:
        """Get a pattern by ID."""
        return self._patterns.get(pattern_id)
    
    def get_compiled(self, pattern_id: str) -> Optional[re.Pattern]:
        """Get compiled regex for a pattern."""
        return self._compiled.get(pattern_id)
    
    def get_by_category(self, category: str) -> List[DetectionPattern]:
        """Get all patterns in a category."""
        pattern_ids = self._categories.get(category, [])
        return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]
    
    def get_enabled(self) -> List[DetectionPattern]:
        """Get all enabled patterns."""
        return [p for p in self._patterns.values() if p.enabled]
    
    def list_categories(self) -> List[str]:
        """List all registered categories."""
        return list(self._categories.keys())
    
    def enable(self, pattern_id: str) -> bool:
        """Enable a pattern."""
        if pattern_id in self._patterns:
            self._patterns[pattern_id].enabled = True
            return True
        return False
    
    def disable(self, pattern_id: str) -> bool:
        """Disable a pattern."""
        if pattern_id in self._patterns:
            self._patterns[pattern_id].enabled = False
            return True
        return False
    
    def match_all(
        self,
        text: str,
        category: Optional[str] = None,
    ) -> Dict[str, List[re.Match]]:
        """Match all patterns against text.
        
        Args:
            text: Text to match against
            category: Optional category filter
            
        Returns:
            Dict of pattern_id -> list of matches
        """
        results = {}
        
        patterns = (
            self.get_by_category(category) if category
            else self.get_enabled()
        )
        
        for pattern in patterns:
            if not pattern.enabled:
                continue
            
            compiled = self._compiled.get(pattern.id)
            if compiled:
                matches = list(compiled.finditer(text))
                if matches:
                    results[pattern.id] = matches
        
        return results
    
    def export_patterns(self) -> List[Dict]:
        """Export all patterns as dictionaries."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "pattern": p.pattern,
                "description": p.description,
                "severity": p.severity.value,
                "category": p.category,
                "enabled": p.enabled,
                "version": p.version,
                "author": p.author,
            }
            for p in self._patterns.values()
        ]
    
    def import_patterns(self, patterns: List[Dict]) -> int:
        """Import patterns from dictionaries.
        
        Args:
            patterns: List of pattern dicts
            
        Returns:
            Number of patterns imported
        """
        imported = 0
        for p_dict in patterns:
            try:
                pattern = DetectionPattern(
                    id=p_dict["id"],
                    name=p_dict["name"],
                    pattern=p_dict["pattern"],
                    description=p_dict.get("description", ""),
                    severity=Severity(p_dict.get("severity", "medium")),
                    category=p_dict.get("category", "custom"),
                    enabled=p_dict.get("enabled", True),
                    version=p_dict.get("version", "1.0.0"),
                    author=p_dict.get("author", "import"),
                )
                if self.register(pattern):
                    imported += 1
            except (KeyError, ValueError):
                continue
        
        return imported


# Global default registry
default_registry = PatternRegistry()
