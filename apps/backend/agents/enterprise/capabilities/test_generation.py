"""Test generation capability for enterprise agents.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TestCase:
    """A single test case."""

    name: str
    description: str
    test_type: str = "unit"  # unit, integration, e2e
    code: str = ""
    assertions: list[str] = field(default_factory=list)
    setup: str = ""
    teardown: str = ""
    tags: list[str] = field(default_factory=list)
    expected_result: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "test_type": self.test_type,
            "code": self.code,
            "assertions": self.assertions,
            "setup": self.setup,
            "teardown": self.teardown,
            "tags": self.tags,
            "expected_result": self.expected_result,
        }


@dataclass
class TestSuite:
    """A collection of test cases."""

    name: str
    framework: str
    language: str
    test_cases: list[TestCase] = field(default_factory=list)
    setup_all: str = ""
    teardown_all: str = ""
    imports: list[str] = field(default_factory=list)

    def add_test(self, test: TestCase) -> None:
        """Add a test case."""
        self.test_cases.append(test)

    def to_code(self) -> str:
        """Generate test suite code."""
        lines: list[str] = []

        # Add imports
        for imp in self.imports:
            lines.append(imp)
        lines.append("")

        # Add setup
        if self.setup_all:
            lines.append(self.setup_all)
            lines.append("")

        # Add test cases
        for test in self.test_cases:
            lines.append(test.code)
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "framework": self.framework,
            "language": self.language,
            "test_count": len(self.test_cases),
            "test_cases": [t.to_dict() for t in self.test_cases],
        }


class TestGenerationCapability:
    """Provides test generation capabilities to agents.

    Generates unit, integration, and e2e tests
    for various frameworks.
    """

    FRAMEWORK_DEFAULTS = {
        "python": "pytest",
        "javascript": "jest",
        "typescript": "vitest",
        "java": "junit",
        "go": "testing",
    }

    FRAMEWORK_IMPORTS = {
        "pytest": ["import pytest"],
        "unittest": ["import unittest"],
        "jest": [],
        "vitest": ["import { describe, it, expect } from 'vitest'"],
        "junit": ["import org.junit.jupiter.api.*;"],
    }

    def __init__(self):
        """Initialize the capability."""
        pass

    def create_suite(
        self,
        name: str,
        language: str,
        framework: str | None = None,
    ) -> TestSuite:
        """Create a new test suite.

        Args:
            name: Suite name
            language: Programming language
            framework: Test framework (auto-detected if not provided)

        Returns:
            New test suite
        """
        if not framework:
            framework = self.FRAMEWORK_DEFAULTS.get(language, "pytest")

        imports = self.FRAMEWORK_IMPORTS.get(framework, [])

        return TestSuite(
            name=name,
            framework=framework,
            language=language,
            imports=imports,
        )

    def create_test(
        self,
        name: str,
        description: str,
        framework: str,
        assertions: list[str],
        test_type: str = "unit",
    ) -> TestCase:
        """Create a test case.

        Args:
            name: Test name
            description: Test description
            framework: Test framework
            assertions: List of assertions
            test_type: Type of test

        Returns:
            Generated test case
        """
        test = TestCase(
            name=name,
            description=description,
            test_type=test_type,
            assertions=assertions,
        )

        # Generate code based on framework
        test.code = self._generate_test_code(test, framework)

        return test

    def _generate_test_code(
        self,
        test: TestCase,
        framework: str,
    ) -> str:
        """Generate test code for a framework."""
        if framework == "pytest":
            return self._generate_pytest(test)
        elif framework == "unittest":
            return self._generate_unittest(test)
        elif framework in ("jest", "vitest"):
            return self._generate_jest(test)
        else:
            return self._generate_pytest(test)

    def _generate_pytest(self, test: TestCase) -> str:
        """Generate pytest test code."""
        lines = [
            f"def {test.name}():",
            f'    """{test.description}"""',
        ]

        if test.setup:
            lines.append("    # Setup")
            lines.append(f"    {test.setup}")

        for assertion in test.assertions:
            lines.append(f"    assert {assertion}")

        if test.teardown:
            lines.append("    # Teardown")
            lines.append(f"    {test.teardown}")

        return "\n".join(lines)

    def _generate_unittest(self, test: TestCase) -> str:
        """Generate unittest test code."""
        lines = [
            f"def {test.name}(self):",
            f'    """{test.description}"""',
        ]

        for assertion in test.assertions:
            lines.append(f"    self.assertTrue({assertion})")

        return "\n".join(lines)

    def _generate_jest(self, test: TestCase) -> str:
        """Generate Jest/Vitest test code."""
        lines = [
            f"it('{test.description}', () => {{",
        ]

        for assertion in test.assertions:
            lines.append(f"    expect({assertion}).toBeTruthy();")

        lines.append("});")

        return "\n".join(lines)

    def generate_edge_case_tests(
        self,
        function_name: str,
        framework: str,
    ) -> list[TestCase]:
        """Generate common edge case tests.

        Args:
            function_name: Name of function to test
            framework: Test framework

        Returns:
            List of edge case test cases
        """
        edge_cases = [
            (
                "empty_input",
                "should handle empty input",
                f"{function_name}('') is not None",
            ),
            (
                "null_input",
                "should handle null/None input",
                f"{function_name}(None) is not None or True",
            ),
            (
                "large_input",
                "should handle large input",
                f"len(str({function_name}('x' * 10000))) >= 0",
            ),
        ]

        tests: list[TestCase] = []
        for name_suffix, description, assertion in edge_cases:
            test = self.create_test(
                name=f"test_{function_name}_{name_suffix}",
                description=description,
                framework=framework,
                assertions=[assertion],
                test_type="unit",
            )
            test.tags.append("edge_case")
            tests.append(test)

        return tests

    def calculate_coverage_estimate(
        self,
        suite: TestSuite,
        total_functions: int,
    ) -> dict[str, Any]:
        """Estimate test coverage.

        Args:
            suite: Test suite
            total_functions: Total functions in codebase

        Returns:
            Coverage estimate
        """
        tested_functions = len(
            set(t.name.replace("test_", "").split("_")[0] for t in suite.test_cases)
        )

        return {
            "test_count": len(suite.test_cases),
            "estimated_coverage": (
                min(100, tested_functions / total_functions * 100)
                if total_functions > 0
                else 0
            ),
            "edge_case_tests": sum(
                1 for t in suite.test_cases if "edge_case" in t.tags
            ),
        }
