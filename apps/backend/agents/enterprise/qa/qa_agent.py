"""QA Agent for test generation and quality assurance.

World-Class Standards:
- 80%+ coverage generation target
- Multi-framework support
- LLM-agnostic test generation

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import json
import uuid

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import (
    CoverageAnalysis,
    EnterpriseAgentType,
    TestCase,
    TestGenerationResult,
)
from .test_generator import TestGenerator, GeneratedTest
from .coverage_analyzer import CoverageAnalyzer, CoverageReport
from .test_templates import TestTemplates


class QAAgent(BaseEnterpriseAgent):
    """Agent for test generation using configured LLM.
    
    Provides comprehensive QA capabilities including:
    - Unit test generation
    - Integration test generation
    - Coverage analysis
    - Test plan generation
    
    Attributes:
        test_generator: Test code generator
        coverage_analyzer: Coverage analysis utility
        templates: Test templates by framework
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.QA
    AGENT_CATEGORY: ClassVar[str] = "qa"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert QA engineer with deep knowledge of:
1. Test-driven development (TDD)
2. Unit, integration, and e2e testing
3. Multiple test frameworks (pytest, Jest, Vitest, etc.)
4. Code coverage and test quality metrics
5. Edge case identification

Generate comprehensive tests that achieve high coverage.
Focus on edge cases and error conditions.
Write clean, maintainable test code."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the QA agent."""
        super().__init__(config, llm_router)
        
        # Add QA capability
        self.add_capability(AgentCapability.TEST_GENERATION)
        
        # Initialize components
        self.test_generator = TestGenerator()
        self.coverage_analyzer = CoverageAnalyzer()
        self.templates = TestTemplates()
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "QA agent that generates comprehensive tests, analyzes coverage, "
            "and creates test plans. Targets 80%+ coverage with edge case focus. "
            "Uses configured LLM provider for intelligent test generation."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute QA task based on context.
        
        Args:
            context: Must contain 'code' and 'language', optionally 'framework'
            
        Returns:
            Test generation results
        """
        if "code" not in context or "language" not in context:
            return {
                "status": "error",
                "message": "Context must contain 'code' and 'language'",
            }
        
        code = context["code"]
        language = context["language"]
        framework = context.get("framework", self._default_framework(language))
        
        result = await self.generate_tests(
            code=code,
            language=language,
            framework=framework,
        )
        
        return {
            "status": "success",
            "test_code": result,
            "framework": framework,
            "language": language,
        }
    
    async def generate_tests(
        self,
        code: str,
        language: str,
        framework: str,
    ) -> str:
        """Generate tests for code.
        
        Args:
            code: Source code to generate tests for
            language: Programming language
            framework: Test framework (pytest, jest, etc.)
            
        Returns:
            Generated test code
        """
        # Get template for framework
        template = self.templates.get_template(framework)
        
        prompt = f"""Generate comprehensive tests for the following {language} code.

Source Code:
```{language}
{code}
```

Test Framework: {framework}

{template.instructions if template else ""}

Requirements:
1. Achieve at least 80% code coverage
2. Test all public functions/methods
3. Include edge cases and error conditions
4. Use descriptive test names
5. Add assertions for all expected behaviors
6. Mock external dependencies

Provide only the test code, ready to run."""
        
        return await self.complete(prompt)
    
    async def analyze_coverage(
        self,
        coverage_report: Dict[str, Any],
    ) -> CoverageAnalysis:
        """Analyze coverage report.
        
        Args:
            coverage_report: Coverage data from test run
            
        Returns:
            Coverage analysis with recommendations
        """
        report = self.coverage_analyzer.analyze(coverage_report)
        
        if report.coverage_percentage < 80:
            # Get LLM recommendations for improving coverage
            prompt = f"""Analyze this coverage report and suggest improvements.

Coverage: {report.coverage_percentage:.1f}%
Uncovered Lines: {report.uncovered_lines[:20]}  # First 20
Files with low coverage:
{json.dumps(report.low_coverage_files, indent=2)}

Provide specific recommendations to improve coverage to 80%+.
"""
            
            recommendations = await self.complete(prompt)
            report.recommendations = recommendations.split("\n")
        
        return CoverageAnalysis(
            total_lines=report.total_lines,
            covered_lines=report.covered_lines,
            coverage_percentage=report.coverage_percentage,
            uncovered_lines=report.uncovered_lines,
            branch_coverage=report.branch_coverage,
            function_coverage=report.function_coverage,
            file_coverage=report.file_coverage,
            recommendations=report.recommendations,
        )
    
    async def suggest_test_cases(
        self,
        code: str,
    ) -> List[TestCase]:
        """Suggest test cases for code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of suggested test cases
        """
        prompt = f"""Analyze this code and suggest test cases.

```
{code}
```

Provide test cases in JSON format:
{{
  "test_cases": [
    {{
      "name": "test_function_name_scenario",
      "description": "What this test verifies",
      "test_type": "unit|integration|e2e",
      "target_function": "function_name",
      "assertions": ["Expected behavior 1", "Expected behavior 2"],
      "edge_case": true|false
    }}
  ]
}}

Include:
- Happy path tests
- Edge cases
- Error conditions
- Boundary tests
"""
        
        response = await self.complete(prompt)
        return self._parse_test_cases(response)
    
    async def generate_test_plan(
        self,
        feature_spec: str,
    ) -> Dict[str, Any]:
        """Generate a test plan from feature specification.
        
        Args:
            feature_spec: Feature specification or requirements
            
        Returns:
            Comprehensive test plan
        """
        prompt = f"""Create a comprehensive test plan for this feature.

Feature Specification:
{feature_spec}

Provide a test plan in JSON format:
{{
  "test_plan": {{
    "overview": "Test plan overview",
    "scope": ["What's in scope"],
    "out_of_scope": ["What's out of scope"],
    "test_categories": [
      {{
        "category": "Unit Tests",
        "tests": [
          {{
            "id": "UT-001",
            "name": "Test name",
            "description": "What it tests",
            "priority": "high|medium|low"
          }}
        ]
      }}
    ],
    "test_environments": ["Required environments"],
    "acceptance_criteria": ["Criteria for passing"]
  }}
}}
"""
        
        response = await self.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("test_plan", {})
        except json.JSONDecodeError:
            return {
                "overview": "Test plan generated from feature spec",
                "raw_response": response,
            }
    
    def _default_framework(self, language: str) -> str:
        """Get default test framework for language."""
        defaults = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "vitest",
            "java": "junit",
            "go": "testing",
            "rust": "cargo-test",
        }
        return defaults.get(language, "pytest")
    
    def _parse_test_cases(self, response: str) -> List[TestCase]:
        """Parse test cases from LLM response."""
        test_cases: List[TestCase] = []
        
        try:
            data = json.loads(response)
            for tc in data.get("test_cases", []):
                test_cases.append(TestCase(
                    id=str(uuid.uuid4()),
                    name=tc.get("name", ""),
                    description=tc.get("description", ""),
                    test_type=tc.get("test_type", "unit"),
                    target_function=tc.get("target_function", ""),
                    test_code="",  # To be generated
                    assertions=tc.get("assertions", []),
                    tags=["edge_case"] if tc.get("edge_case") else [],
                ))
        except json.JSONDecodeError:
            pass
        
        return test_cases
