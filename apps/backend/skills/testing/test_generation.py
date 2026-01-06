"""Test generation skill.

Generates unit and integration tests for code.

Capabilities:
- Generate unit tests
- Generate integration tests
- Support multiple test frameworks
- Generate test data/fixtures
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class TestFramework(Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"
    NUNIT = "nunit"
    XUNIT = "xunit"
    RSPEC = "rspec"
    GO_TEST = "go_test"


class TestType(Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PROPERTY = "property"
    SNAPSHOT = "snapshot"


@dataclass
class GeneratedTest:
    """A generated test case."""
    name: str
    code: str
    test_type: TestType
    description: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_output: Optional[Any] = None


class TestGenerationSkill(BaseSkill):
    """Generate tests for code.
    
    Uses LLM to analyze code and generate comprehensive test cases
    covering various scenarios including edge cases.
    
    Example:
        skill = TestGenerationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def add(a, b): return a + b",
                "framework": "pytest",
                "test_types": ["unit"],
                "coverage_target": 80,
            }
        )
        result = await skill.run(context)
    """
    
    name = "test_generation"
    description = "Generate unit and integration tests"
    category = SkillCategory.TESTING
    required_tools = ["file_read", "file_write"]
    required_permissions = {"read_files", "write_files", "llm_access"}
    version = "1.0.0"
    
    # Framework to language mapping
    FRAMEWORK_LANGUAGES = {
        TestFramework.PYTEST: "python",
        TestFramework.UNITTEST: "python",
        TestFramework.JEST: "javascript",
        TestFramework.MOCHA: "javascript",
        TestFramework.JUNIT: "java",
        TestFramework.NUNIT: "csharp",
        TestFramework.XUNIT: "csharp",
        TestFramework.RSPEC: "ruby",
        TestFramework.GO_TEST: "go",
    }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        if not input_data.get("code", "").strip():
            return False
        return True
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute test generation.
        
        Args:
            context: Execution context with code to test
            
        Returns:
            SkillResult with generated tests
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        framework = input_data.get("framework", "pytest")
        test_types = input_data.get("test_types", ["unit"])
        coverage_target = input_data.get("coverage_target", 80)
        
        # Analyze code to identify testable units
        testable_units = self._analyze_testable_units(code)
        
        # Generate tests for each unit
        generated_tests = []
        for unit in testable_units:
            tests = self._generate_tests_for_unit(unit, framework, test_types)
            generated_tests.extend(tests)
        
        # Combine into test file
        test_code = self._combine_tests(generated_tests, framework)
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "test_code": test_code,
                "framework": framework,
                "test_count": len(generated_tests),
                "tests": [self._test_to_dict(t) for t in generated_tests],
                "coverage_target": coverage_target,
            },
            tokens_used=0,
        )
    
    def _analyze_testable_units(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code to find testable units."""
        # Placeholder - will use AST analysis
        units = []
        
        # Simple function detection
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("def ") or line.strip().startswith("async def "):
                name = line.split("(")[0].split(" ")[-1]
                units.append({
                    "name": name,
                    "type": "function",
                    "line": i + 1,
                    "code": line,
                })
        
        return units
    
    def _generate_tests_for_unit(
        self,
        unit: Dict[str, Any],
        framework: str,
        test_types: List[str],
    ) -> List[GeneratedTest]:
        """Generate tests for a single unit."""
        tests = []
        
        # Generate a basic test
        test_name = f"test_{unit['name']}"
        test_code = self._generate_test_code(unit, framework)
        
        tests.append(GeneratedTest(
            name=test_name,
            code=test_code,
            test_type=TestType.UNIT,
            description=f"Test for {unit['name']}",
        ))
        
        return tests
    
    def _generate_test_code(self, unit: Dict[str, Any], framework: str) -> str:
        """Generate test code for a unit."""
        if framework in ("pytest", "unittest"):
            return f'''def test_{unit["name"]}_basic():
    """Test {unit["name"]} with basic inputs."""
    # TODO: Add test implementation
    pass

def test_{unit["name"]}_edge_cases():
    """Test {unit["name"]} edge cases."""
    # TODO: Add edge case tests
    pass
'''
        else:
            return f"// Test for {unit['name']}\n"
    
    def _combine_tests(self, tests: List[GeneratedTest], framework: str) -> str:
        """Combine generated tests into a test file."""
        if framework == "pytest":
            header = '''"""Generated tests.

Auto-generated test suite.
"""
import pytest

'''
        elif framework == "unittest":
            header = '''"""Generated tests."""
import unittest

'''
        else:
            header = "// Generated tests\n\n"
        
        test_code = header + "\n\n".join(t.code for t in tests)
        return test_code
    
    def _test_to_dict(self, test: GeneratedTest) -> Dict[str, Any]:
        """Convert GeneratedTest to dictionary."""
        return {
            "name": test.name,
            "test_type": test.test_type.value,
            "description": test.description,
        }
