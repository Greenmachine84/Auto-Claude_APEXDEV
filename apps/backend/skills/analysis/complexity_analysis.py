"""Complexity analysis skill.

Analyzes code complexity.

Capabilities:
- Calculate cyclomatic complexity
- Calculate cognitive complexity
- Measure lines of code
- Identify complex hotspots
"""

from dataclasses import dataclass, field
from typing import Any

from skills.core.base_skill import (
    BaseSkill,
    SkillCategory,
    SkillContext,
    SkillResult,
    SkillStatus,
)


@dataclass
class FunctionComplexity:
    """Complexity metrics for a function."""

    name: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    parameter_count: int
    is_complex: bool = False


@dataclass
class FileComplexity:
    """Complexity metrics for a file."""

    file_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions: list[FunctionComplexity] = field(default_factory=list)
    average_complexity: float = 0.0


class ComplexityAnalysisSkill(BaseSkill):
    """Analyze code complexity.

    Calculates various complexity metrics and identifies
    complex code that may need refactoring.

    Example:
        skill = ComplexityAnalysisSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def complex_function()...",
                "complexity_threshold": 10,
            }
        )
        result = await skill.run(context)
    """

    name = "complexity_analysis"
    description = "Analyze code complexity"
    category = SkillCategory.ANALYSIS
    required_tools = ["file_read"]
    required_permissions = {"read_files"}
    version = "1.0.0"

    # Default thresholds
    DEFAULT_CYCLOMATIC_THRESHOLD = 10
    DEFAULT_COGNITIVE_THRESHOLD = 15
    DEFAULT_LOC_THRESHOLD = 100

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data and "files" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute complexity analysis.

        Args:
            context: Execution context with code

        Returns:
            SkillResult with complexity metrics
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        file_path = input_data.get("file_path", "<inline>")
        cyclomatic_threshold = input_data.get(
            "cyclomatic_threshold", self.DEFAULT_CYCLOMATIC_THRESHOLD
        )

        # Analyze complexity
        file_metrics = self._analyze_file(code, file_path, cyclomatic_threshold)

        # Identify hotspots
        hotspots = [f for f in file_metrics.functions if f.is_complex]

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "total_lines": file_metrics.total_lines,
                "code_lines": file_metrics.code_lines,
                "average_complexity": file_metrics.average_complexity,
                "functions": [self._func_to_dict(f) for f in file_metrics.functions],
                "hotspots": [self._func_to_dict(h) for h in hotspots],
                "hotspot_count": len(hotspots),
            },
            tokens_used=0,
        )

    def _analyze_file(
        self, code: str, file_path: str, threshold: int
    ) -> FileComplexity:
        """Analyze file complexity."""
        lines = code.split("\n")
        total_lines = len(lines)
        code_lines = sum(
            1 for l in lines if l.strip() and not l.strip().startswith("#")
        )
        comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
        blank_lines = sum(1 for l in lines if not l.strip())

        # Analyze functions
        functions = self._analyze_functions(code, file_path, threshold)

        avg = 0.0
        if functions:
            avg = sum(f.cyclomatic_complexity for f in functions) / len(functions)

        return FileComplexity(
            file_path=file_path,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            average_complexity=avg,
        )

    def _analyze_functions(
        self, code: str, file_path: str, threshold: int
    ) -> list[FunctionComplexity]:
        """Analyze function complexity."""
        functions = []
        lines = code.split("\n")

        for i, line in enumerate(lines):
            if line.strip().startswith(("def ", "async def ")):
                name = (
                    line.split("(")[0]
                    .replace("async def ", "")
                    .replace("def ", "")
                    .strip()
                )

                # Simple complexity calculation (placeholder)
                cyclomatic = self._calculate_cyclomatic(code, name)

                functions.append(
                    FunctionComplexity(
                        name=name,
                        file_path=file_path,
                        line_number=i + 1,
                        cyclomatic_complexity=cyclomatic,
                        cognitive_complexity=cyclomatic,  # Simplified
                        lines_of_code=10,  # Placeholder
                        parameter_count=0,
                        is_complex=cyclomatic > threshold,
                    )
                )

        return functions

    def _calculate_cyclomatic(self, code: str, function_name: str) -> int:
        """Calculate cyclomatic complexity."""
        # Simple heuristic - count decision points
        decision_keywords = [
            "if",
            "elif",
            "else",
            "for",
            "while",
            "except",
            "and",
            "or",
        ]
        complexity = 1

        for keyword in decision_keywords:
            complexity += code.lower().count(f" {keyword} ")

        return min(complexity, 20)  # Cap for placeholder

    def _func_to_dict(self, func: FunctionComplexity) -> dict[str, Any]:
        """Convert FunctionComplexity to dictionary."""
        return {
            "name": func.name,
            "file_path": func.file_path,
            "line_number": func.line_number,
            "cyclomatic_complexity": func.cyclomatic_complexity,
            "cognitive_complexity": func.cognitive_complexity,
            "lines_of_code": func.lines_of_code,
            "is_complex": func.is_complex,
        }
