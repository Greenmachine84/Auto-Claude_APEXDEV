"""Coverage analyzer for QA agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CoverageReport:
    """Coverage analysis report."""

    total_lines: int = 0
    covered_lines: int = 0
    coverage_percentage: float = 0.0
    uncovered_lines: list[int] = field(default_factory=list)
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    file_coverage: dict[str, float] = field(default_factory=dict)
    low_coverage_files: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_lines": self.total_lines,
            "covered_lines": self.covered_lines,
            "coverage_percentage": self.coverage_percentage,
            "uncovered_lines": self.uncovered_lines,
            "branch_coverage": self.branch_coverage,
            "function_coverage": self.function_coverage,
            "file_coverage": self.file_coverage,
            "low_coverage_files": self.low_coverage_files,
            "recommendations": self.recommendations,
        }

    @property
    def meets_target(self) -> bool:
        """Check if coverage meets 80% target."""
        return self.coverage_percentage >= 80.0

    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "✅" if self.meets_target else "⚠️"
        return (
            f"{status} Coverage: {self.coverage_percentage:.1f}%\n"
            f"Lines: {self.covered_lines}/{self.total_lines}\n"
            f"Branch: {self.branch_coverage:.1f}%\n"
            f"Function: {self.function_coverage:.1f}%"
        )


class CoverageAnalyzer:
    """Analyzes code coverage reports.

    Parses coverage data and provides recommendations
    for improving coverage.
    """

    TARGET_COVERAGE = 80.0  # World-class standard: 80%+

    def analyze(self, coverage_data: dict[str, Any]) -> CoverageReport:
        """Analyze coverage data.

        Args:
            coverage_data: Coverage report data (e.g., from pytest-cov)

        Returns:
            Analyzed coverage report
        """
        report = CoverageReport()

        # Parse standard coverage.py/pytest-cov format
        if "totals" in coverage_data:
            totals = coverage_data["totals"]
            report.total_lines = totals.get("num_statements", 0)
            report.covered_lines = totals.get("covered_lines", 0)
            report.coverage_percentage = totals.get("percent_covered", 0.0)
        elif "summary" in coverage_data:
            summary = coverage_data["summary"]
            report.total_lines = summary.get("lines_total", 0)
            report.covered_lines = summary.get("lines_covered", 0)
            if report.total_lines > 0:
                report.coverage_percentage = (
                    report.covered_lines / report.total_lines * 100
                )
        elif "lines" in coverage_data and "covered" in coverage_data:
            # Simple format
            report.total_lines = coverage_data["lines"]
            report.covered_lines = coverage_data["covered"]
            if report.total_lines > 0:
                report.coverage_percentage = (
                    report.covered_lines / report.total_lines * 100
                )

        # Parse file-level coverage
        files = coverage_data.get("files", {})
        for file_path, file_data in files.items():
            if isinstance(file_data, dict):
                pct = file_data.get("summary", {}).get("percent_covered", 0)
                report.file_coverage[file_path] = pct

                if pct < self.TARGET_COVERAGE:
                    report.low_coverage_files.append(
                        {
                            "file": file_path,
                            "coverage": pct,
                            "missing": file_data.get("missing_lines", []),
                        }
                    )

        # Parse uncovered lines
        if "missing" in coverage_data:
            report.uncovered_lines = coverage_data["missing"]
        elif "uncovered_lines" in coverage_data:
            report.uncovered_lines = coverage_data["uncovered_lines"]

        # Parse branch and function coverage
        report.branch_coverage = coverage_data.get("branch_coverage", 0.0)
        report.function_coverage = coverage_data.get("function_coverage", 0.0)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: CoverageReport) -> list[str]:
        """Generate coverage improvement recommendations."""
        recommendations: list[str] = []

        if not report.meets_target:
            gap = self.TARGET_COVERAGE - report.coverage_percentage
            recommendations.append(
                f"Coverage is {gap:.1f}% below target of {self.TARGET_COVERAGE}%"
            )

        if report.low_coverage_files:
            files = [f["file"] for f in report.low_coverage_files[:3]]
            recommendations.append(
                f"Focus on improving coverage in: {', '.join(files)}"
            )

        if report.branch_coverage < 70:
            recommendations.append(
                "Branch coverage is low. Add tests for conditional logic."
            )

        if report.function_coverage < 80:
            recommendations.append(
                "Function coverage is low. Add tests for untested functions."
            )

        if len(report.uncovered_lines) > 20:
            recommendations.append(
                f"{len(report.uncovered_lines)} lines are not covered. "
                "Consider adding targeted tests."
            )

        return recommendations

    def calculate_delta(
        self,
        old_report: CoverageReport,
        new_report: CoverageReport,
    ) -> dict[str, float]:
        """Calculate coverage change between two reports.

        Args:
            old_report: Previous coverage report
            new_report: Current coverage report

        Returns:
            Coverage delta metrics
        """
        return {
            "coverage_delta": (
                new_report.coverage_percentage - old_report.coverage_percentage
            ),
            "lines_delta": new_report.covered_lines - old_report.covered_lines,
            "branch_delta": new_report.branch_coverage - old_report.branch_coverage,
            "function_delta": (
                new_report.function_coverage - old_report.function_coverage
            ),
        }

    def identify_high_impact_files(
        self,
        report: CoverageReport,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Identify files where adding tests would have highest impact.

        Args:
            report: Coverage report
            limit: Maximum files to return

        Returns:
            List of high-impact files
        """
        # Sort by coverage (lowest first)
        sorted_files = sorted(report.low_coverage_files, key=lambda x: x["coverage"])

        return sorted_files[:limit]
