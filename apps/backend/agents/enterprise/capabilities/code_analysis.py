"""Code analysis capability for enterprise agents.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import ast
import re


@dataclass
class AnalysisResult:
    """Result of code analysis."""
    file_path: str
    language: str
    lines_of_code: int = 0
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "lines_of_code": self.lines_of_code,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "complexity": self.complexity,
            "issues": self.issues,
            "metrics": self.metrics,
        }


class CodeAnalyzer(Protocol):
    """Protocol for code analyzers."""
    
    def analyze(self, code: str, file_path: str) -> AnalysisResult:
        """Analyze code and return results."""
        ...


class CodeAnalysisCapability:
    """Provides code analysis capabilities to agents.
    
    Analyzes code for structure, complexity, and quality metrics.
    Language-agnostic design with specialized analyzers.
    """
    
    LANGUAGE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
    }
    
    def __init__(self):
        """Initialize the capability."""
        pass
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        for ext, lang in self.LANGUAGE_EXTENSIONS.items():
            if file_path.endswith(ext):
                return lang
        return "unknown"
    
    def analyze(
        self,
        code: str,
        file_path: str,
    ) -> AnalysisResult:
        """Analyze code.
        
        Args:
            code: Source code
            file_path: File path for language detection
            
        Returns:
            Analysis result
        """
        language = self.detect_language(file_path)
        
        result = AnalysisResult(
            file_path=file_path,
            language=language,
            lines_of_code=self._count_lines(code),
        )
        
        if language == "python":
            self._analyze_python(code, result)
        elif language in ("javascript", "typescript"):
            self._analyze_javascript(code, result)
        else:
            self._analyze_generic(code, result)
        
        # Calculate complexity
        result.complexity = self._calculate_complexity(code, language)
        
        # Calculate metrics
        result.metrics = self._calculate_metrics(result)
        
        return result
    
    def _count_lines(self, code: str) -> int:
        """Count non-empty lines of code."""
        lines = code.split("\n")
        return sum(1 for line in lines if line.strip())
    
    def _analyze_python(self, code: str, result: AnalysisResult) -> None:
        """Analyze Python code."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    result.classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result.imports.append(node.module)
        except SyntaxError:
            result.issues.append({
                "type": "syntax_error",
                "message": "Failed to parse Python code",
            })
    
    def _analyze_javascript(self, code: str, result: AnalysisResult) -> None:
        """Analyze JavaScript/TypeScript code."""
        # Function detection
        func_patterns = [
            r"function\s+(\w+)",
            r"const\s+(\w+)\s*=\s*(?:async\s+)?function",
            r"const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>",
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, code):
                result.functions.append(match.group(1))
        
        # Class detection
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, code):
            result.classes.append(match.group(1))
        
        # Import detection
        import_patterns = [
            r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
            r"require\(['\"]([^'\"]+)['\"]\)",
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                result.imports.append(match.group(1))
    
    def _analyze_generic(self, code: str, result: AnalysisResult) -> None:
        """Generic analysis for unknown languages."""
        # Function patterns for common languages
        func_pattern = r"(?:func|function|def|fn)\s+(\w+)"
        for match in re.finditer(func_pattern, code):
            result.functions.append(match.group(1))
        
        # Class patterns
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, code):
            result.classes.append(match.group(1))
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate cyclomatic complexity estimate."""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_patterns = [
            r"\bif\b",
            r"\belif\b",
            r"\belse\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\bcase\b",
            r"\bcatch\b",
            r"\bexcept\b",
            r"\band\b",
            r"\bor\b",
            r"&&",
            r"\|\|",
            r"\?",  # Ternary
        ]
        
        for pattern in decision_patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _calculate_metrics(self, result: AnalysisResult) -> Dict[str, Any]:
        """Calculate code metrics."""
        return {
            "function_count": len(result.functions),
            "class_count": len(result.classes),
            "import_count": len(result.imports),
            "avg_function_length": (
                result.lines_of_code / len(result.functions)
                if result.functions else 0
            ),
            "complexity_per_loc": (
                result.complexity / result.lines_of_code
                if result.lines_of_code > 0 else 0
            ),
        }
    
    def find_code_smells(
        self,
        code: str,
        file_path: str,
    ) -> List[Dict[str, Any]]:
        """Find code smells in code.
        
        Args:
            code: Source code
            file_path: File path
            
        Returns:
            List of code smell findings
        """
        smells: List[Dict[str, Any]] = []
        lines = code.split("\n")
        
        # Long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                smells.append({
                    "type": "long_line",
                    "line": i,
                    "message": f"Line exceeds 120 characters ({len(line)})",
                })
        
        # Long file
        if len(lines) > 500:
            smells.append({
                "type": "long_file",
                "message": f"File has {len(lines)} lines (recommended < 500)",
            })
        
        # Magic numbers
        magic_pattern = r"(?<!\.)\b(?!0\b|1\b)\d{2,}\b(?!\.)"
        for i, line in enumerate(lines, 1):
            if re.search(magic_pattern, line):
                smells.append({
                    "type": "magic_number",
                    "line": i,
                    "message": "Magic number detected",
                })
        
        return smells
    
    def compare(
        self,
        result1: AnalysisResult,
        result2: AnalysisResult,
    ) -> Dict[str, Any]:
        """Compare two analysis results.
        
        Args:
            result1: First analysis
            result2: Second analysis
            
        Returns:
            Comparison metrics
        """
        return {
            "loc_delta": result2.lines_of_code - result1.lines_of_code,
            "complexity_delta": result2.complexity - result1.complexity,
            "functions_added": list(
                set(result2.functions) - set(result1.functions)
            ),
            "functions_removed": list(
                set(result1.functions) - set(result2.functions)
            ),
            "classes_added": list(
                set(result2.classes) - set(result1.classes)
            ),
            "classes_removed": list(
                set(result1.classes) - set(result2.classes)
            ),
        }
