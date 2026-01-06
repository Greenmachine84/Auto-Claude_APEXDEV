"""Coverage analysis skill.

Analyzes test coverage for code.

Capabilities:
- Measure line coverage
- Measure branch coverage
- Identify uncovered code
- Generate coverage reports
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


@dataclass
class CoverageData:
    """Coverage data for a file."""
    file_path: str
    line_coverage: float
    branch_coverage: float
    lines_covered: int
    lines_total: int
    branches_covered: int
    branches_total: int
    uncovered_lines: List[int] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Overall coverage report."""
    total_line_coverage: float
    total_branch_coverage: float
    files: List[CoverageData] = field(default_factory=list)
    
    @property
    def meets_threshold(self) -> bool:
        """Check if coverage meets default threshold (80%)."""
        return self.total_line_coverage >= 80.0


class CoverageAnalysisSkill(BaseSkill):
    """Analyze test coverage.
    
    Runs coverage analysis on the codebase and generates
    detailed reports on code coverage.
    
    Example:
        skill = CoverageAnalysisSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "source_path": "src/",
                "test_path": "tests/",
                "threshold": 80,
            }
        )
        result = await skill.run(context)
    """
    
    name = "coverage_analysis"
    description = "Analyze test coverage"
    category = SkillCategory.TESTING
    required_tools = ["command_execute", "file_read"]
    required_permissions = {"execute_commands", "read_files"}
    version = "1.0.0"
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "source_path" not in input_data:
            return False
        return True
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute coverage analysis.
        
        Args:
            context: Execution context with paths
            
        Returns:
            SkillResult with coverage report
        """
        input_data = context.input_data
        source_path = input_data.get("source_path", "src/")
        test_path = input_data.get("test_path", "tests/")
        threshold = input_data.get("threshold", 80)
        
        # Run coverage analysis (placeholder)
        report = self._analyze_coverage(source_path, test_path)
        
        # Check threshold
        passes_threshold = report.total_line_coverage >= threshold
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "total_line_coverage": report.total_line_coverage,
                "total_branch_coverage": report.total_branch_coverage,
                "threshold": threshold,
                "passes_threshold": passes_threshold,
                "files": [self._coverage_to_dict(f) for f in report.files],
                "file_count": len(report.files),
            },
            tokens_used=0,
        )
    
    def _analyze_coverage(self, source_path: str, test_path: str) -> CoverageReport:
        """Analyze coverage (placeholder)."""
        # Will use coverage tools for actual analysis
        return CoverageReport(
            total_line_coverage=0.0,
            total_branch_coverage=0.0,
            files=[],
        )
    
    def _coverage_to_dict(self, data: CoverageData) -> Dict[str, Any]:
        """Convert CoverageData to dictionary."""
        return {
            "file_path": data.file_path,
            "line_coverage": data.line_coverage,
            "branch_coverage": data.branch_coverage,
            "lines_covered": data.lines_covered,
            "lines_total": data.lines_total,
            "uncovered_lines": data.uncovered_lines,
        }
