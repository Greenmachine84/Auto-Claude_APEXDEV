"""Technical debt analyzer for project analysis.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass
class TechDebtItem:
    """A technical debt item."""
    file_path: str
    line_number: Optional[int] = None
    category: str = ""  # todo, fixme, hack, complexity, duplication, etc.
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    effort: str = "medium"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "effort": self.effort,
        }


@dataclass
class TechDebtReport:
    """Technical debt analysis report."""
    items: List[TechDebtItem] = field(default_factory=list)
    total_score: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_file: Dict[str, int] = field(default_factory=dict)
    
    def add_item(self, item: TechDebtItem) -> None:
        """Add a tech debt item."""
        self.items.append(item)
        
        # Update counts
        self.by_category[item.category] = self.by_category.get(item.category, 0) + 1
        self.by_severity[item.severity] = self.by_severity.get(item.severity, 0) + 1
        self.by_file[item.file_path] = self.by_file.get(item.file_path, 0) + 1
        
        # Update score
        severity_scores = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        self.total_score += severity_scores.get(item.severity, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_items": len(self.items),
            "total_score": self.total_score,
            "by_category": self.by_category,
            "by_severity": self.by_severity,
            "by_file": self.by_file,
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        return (
            f"Technical Debt Report\n"
            f"Total Items: {len(self.items)}\n"
            f"Total Score: {self.total_score}\n"
            f"By Category: {self.by_category}\n"
            f"By Severity: {self.by_severity}"
        )


class TechDebtAnalyzer:
    """Analyzes code for technical debt indicators.
    
    Scans for TODO comments, complexity issues,
    code smells, and other debt indicators.
    """
    
    # Patterns for detecting tech debt
    COMMENT_PATTERNS = {
        "todo": (r"#\s*TODO[:\s]?(.*)$|//\s*TODO[:\s]?(.*)$", "low"),
        "fixme": (r"#\s*FIXME[:\s]?(.*)$|//\s*FIXME[:\s]?(.*)$", "high"),
        "hack": (r"#\s*HACK[:\s]?(.*)$|//\s*HACK[:\s]?(.*)$", "medium"),
        "xxx": (r"#\s*XXX[:\s]?(.*)$|//\s*XXX[:\s]?(.*)$", "medium"),
        "bug": (r"#\s*BUG[:\s]?(.*)$|//\s*BUG[:\s]?(.*)$", "critical"),
        "deprecated": (r"@deprecated|#\s*DEPRECATED", "medium"),
    }
    
    # Code smell patterns
    CODE_SMELLS = {
        "magic_numbers": (
            r"\b(?<!\.)\d{2,}(?!\.\d)\b",  # Numbers with 2+ digits not in floats
            "Magic number detected",
            "low",
        ),
        "long_function": (
            None,  # Handled separately
            "Function exceeds recommended length",
            "medium",
        ),
        "deep_nesting": (
            None,  # Handled separately
            "Deep nesting detected",
            "medium",
        ),
        "broad_exception": (
            r"except\s*:|except\s+Exception\s*:",
            "Broad exception handling",
            "medium",
        ),
        "hardcoded_credentials": (
            r"password\s*=\s*['\"][^'\"]+['\"]|api_key\s*=\s*['\"][^'\"]+['\"]",
            "Possible hardcoded credentials",
            "critical",
        ),
    }
    
    # Thresholds
    MAX_FUNCTION_LINES = 50
    MAX_NESTING_DEPTH = 4
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze(
        self,
        files: Dict[str, str],
    ) -> TechDebtReport:
        """Analyze files for technical debt.
        
        Args:
            files: Map of file paths to contents
            
        Returns:
            Tech debt report
        """
        report = TechDebtReport()
        
        for file_path, content in files.items():
            # Skip non-code files
            if not self._is_code_file(file_path):
                continue
            
            # Check comment patterns
            self._check_comments(file_path, content, report)
            
            # Check code smells
            self._check_code_smells(file_path, content, report)
            
            # Check complexity
            self._check_complexity(file_path, content, report)
        
        return report
    
    def _is_code_file(self, path: str) -> bool:
        """Check if file is a code file."""
        code_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx",
            ".java", ".go", ".rs", ".rb", ".php",
            ".c", ".cpp", ".h", ".cs",
        }
        return any(path.endswith(ext) for ext in code_extensions)
    
    def _check_comments(
        self,
        file_path: str,
        content: str,
        report: TechDebtReport,
    ) -> None:
        """Check for TODO/FIXME type comments."""
        lines = content.split("\n")
        
        for category, (pattern, severity) in self.COMMENT_PATTERNS.items():
            for line_num, line in enumerate(lines, 1):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    description = (
                        match.group(1) or match.group(2) if match.lastindex else line.strip()
                    )
                    report.add_item(TechDebtItem(
                        file_path=file_path,
                        line_number=line_num,
                        category=category,
                        description=description.strip() if description else f"{category.upper()} found",
                        severity=severity,
                        effort="low" if category in ("todo", "xxx") else "medium",
                    ))
    
    def _check_code_smells(
        self,
        file_path: str,
        content: str,
        report: TechDebtReport,
    ) -> None:
        """Check for code smells."""
        for smell, (pattern, description, severity) in self.CODE_SMELLS.items():
            if pattern is None:
                continue  # Handled elsewhere
            
            for match in re.finditer(pattern, content):
                # Find line number
                line_num = content[:match.start()].count("\n") + 1
                
                report.add_item(TechDebtItem(
                    file_path=file_path,
                    line_number=line_num,
                    category=smell,
                    description=description,
                    severity=severity,
                    effort="low",
                ))
    
    def _check_complexity(
        self,
        file_path: str,
        content: str,
        report: TechDebtReport,
    ) -> None:
        """Check for complexity issues."""
        lines = content.split("\n")
        
        # Check for long functions (simplified)
        if file_path.endswith(".py"):
            self._check_python_function_length(file_path, lines, report)
        
        # Check nesting depth
        self._check_nesting_depth(file_path, lines, report)
    
    def _check_python_function_length(
        self,
        file_path: str,
        lines: List[str],
        report: TechDebtReport,
    ) -> None:
        """Check Python function lengths."""
        func_start: Optional[int] = None
        func_name = ""
        func_indent = 0
        
        for i, line in enumerate(lines):
            # Detect function start
            match = re.match(r"^(\s*)(?:async\s+)?def\s+(\w+)", line)
            if match:
                # Check if previous function was too long
                if func_start is not None:
                    length = i - func_start
                    if length > self.MAX_FUNCTION_LINES:
                        report.add_item(TechDebtItem(
                            file_path=file_path,
                            line_number=func_start + 1,
                            category="long_function",
                            description=f"Function '{func_name}' has {length} lines (max: {self.MAX_FUNCTION_LINES})",
                            severity="medium",
                            effort="high",
                        ))
                
                func_start = i
                func_name = match.group(2)
                func_indent = len(match.group(1))
            
            # Detect function end (new function or class at same/lower indent)
            elif func_start is not None:
                if line.strip() and not line.startswith(" " * (func_indent + 1)):
                    if re.match(r"^\s*(class|def|async\s+def)\s", line):
                        length = i - func_start
                        if length > self.MAX_FUNCTION_LINES:
                            report.add_item(TechDebtItem(
                                file_path=file_path,
                                line_number=func_start + 1,
                                category="long_function",
                                description=f"Function '{func_name}' has {length} lines",
                                severity="medium",
                                effort="high",
                            ))
                        func_start = None
    
    def _check_nesting_depth(
        self,
        file_path: str,
        lines: List[str],
        report: TechDebtReport,
    ) -> None:
        """Check for deep nesting."""
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Count leading spaces
            spaces = len(line) - len(line.lstrip())
            indent_level = spaces // 4  # Assuming 4-space indentation
            
            if indent_level > self.MAX_NESTING_DEPTH:
                # Only report once per region
                if i == 0 or not self._is_deeply_nested(lines[i-1]):
                    report.add_item(TechDebtItem(
                        file_path=file_path,
                        line_number=i + 1,
                        category="deep_nesting",
                        description=f"Nesting depth {indent_level} exceeds maximum {self.MAX_NESTING_DEPTH}",
                        severity="medium",
                        effort="medium",
                    ))
    
    def _is_deeply_nested(self, line: str) -> bool:
        """Check if a line is deeply nested."""
        if not line.strip():
            return False
        spaces = len(line) - len(line.lstrip())
        return spaces // 4 > self.MAX_NESTING_DEPTH
