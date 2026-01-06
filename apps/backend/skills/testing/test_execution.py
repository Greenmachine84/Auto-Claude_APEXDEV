"""Test execution skill.

Executes tests and collects results.

Capabilities:
- Run test suites
- Collect test results
- Parse test output
- Track test duration
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class TestOutcome(Enum):
    """Possible test outcomes."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"  # Expected failure
    XPASS = "xpass"  # Unexpected pass


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    outcome: TestOutcome
    duration_seconds: float
    message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Result of running a test suite."""
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_seconds: float
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total == 0:
            return 0.0
        return self.passed / self.total * 100


class TestExecutionSkill(BaseSkill):
    """Execute tests and collect results.
    
    Runs test suites using the specified framework and collects
    detailed results including failures and timing.
    
    Example:
        skill = TestExecutionSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "test_path": "tests/",
                "framework": "pytest",
                "args": ["-v", "--tb=short"],
            }
        )
        result = await skill.run(context)
    """
    
    name = "test_execution"
    description = "Execute tests and collect results"
    category = SkillCategory.TESTING
    required_tools = ["command_execute", "file_read"]
    required_permissions = {"execute_commands", "read_files"}
    version = "1.0.0"
    
    # Framework commands
    FRAMEWORK_COMMANDS = {
        "pytest": "pytest",
        "unittest": "python -m unittest",
        "jest": "npx jest",
        "mocha": "npx mocha",
        "go_test": "go test",
    }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "test_path" not in input_data:
            return False
        return True
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute tests.
        
        Args:
            context: Execution context with test configuration
            
        Returns:
            SkillResult with test results
        """
        input_data = context.input_data
        test_path = input_data.get("test_path", "tests/")
        framework = input_data.get("framework", "pytest")
        args = input_data.get("args", [])
        timeout = input_data.get("timeout", 300)
        
        # Build test command
        command = self._build_command(framework, test_path, args)
        
        # Execute tests (placeholder - will use terminal tool)
        start_time = datetime.utcnow()
        output = self._execute_tests(command, timeout)
        end_time = datetime.utcnow()
        
        # Parse results
        suite_result = self._parse_results(output, framework)
        suite_result.duration_seconds = (end_time - start_time).total_seconds()
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "total": suite_result.total,
                "passed": suite_result.passed,
                "failed": suite_result.failed,
                "skipped": suite_result.skipped,
                "errors": suite_result.errors,
                "success_rate": suite_result.success_rate,
                "duration_seconds": suite_result.duration_seconds,
                "results": [self._result_to_dict(r) for r in suite_result.results],
                "command": command,
            },
            tokens_used=0,
        )
    
    def _build_command(self, framework: str, test_path: str, args: List[str]) -> str:
        """Build test execution command."""
        base = self.FRAMEWORK_COMMANDS.get(framework, "pytest")
        arg_str = " ".join(args) if args else ""
        return f"{base} {test_path} {arg_str}".strip()
    
    def _execute_tests(self, command: str, timeout: int) -> str:
        """Execute tests and return output (placeholder)."""
        # Will use terminal tool for actual execution
        return "Collected 0 tests\n"
    
    def _parse_results(self, output: str, framework: str) -> TestSuiteResult:
        """Parse test output to extract results."""
        # Placeholder parsing
        return TestSuiteResult(
            total=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            duration_seconds=0.0,
        )
    
    def _result_to_dict(self, result: TestResult) -> Dict[str, Any]:
        """Convert TestResult to dictionary."""
        return {
            "name": result.name,
            "outcome": result.outcome.value,
            "duration_seconds": result.duration_seconds,
            "message": result.message,
        }
