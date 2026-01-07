"""Test templates for different frameworks.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TestTemplate:
    """Template for a test framework."""
    framework: str
    language: str
    file_extension: str
    import_statement: str
    test_function_prefix: str
    assertion_style: str  # "assert", "expect", "assertEquals"
    instructions: str
    example: str
    setup_code: str = ""
    teardown_code: str = ""
    
    def get_test_file_name(self, source_file: str) -> str:
        """Generate test file name from source file."""
        base = source_file.rsplit(".", 1)[0]
        if self.framework in ("pytest", "unittest"):
            return f"test_{base}{self.file_extension}"
        elif self.framework in ("jest", "vitest", "mocha"):
            return f"{base}.test{self.file_extension}"
        else:
            return f"test_{base}{self.file_extension}"


class TestTemplates:
    """Collection of test templates for different frameworks."""
    
    def __init__(self):
        """Initialize with default templates."""
        self._templates: Dict[str, TestTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load default test templates."""
        # Python - pytest
        self._templates["pytest"] = TestTemplate(
            framework="pytest",
            language="python",
            file_extension=".py",
            import_statement="import pytest",
            test_function_prefix="test_",
            assertion_style="assert",
            instructions="""
Generate pytest-style tests:
- Use 'def test_function_name()' naming
- Use plain 'assert' statements
- Use @pytest.fixture for shared setup
- Use @pytest.mark.parametrize for multiple cases
- Use pytest.raises for exception testing
""",
            example="""
import pytest
from module import function_to_test


def test_function_success():
    result = function_to_test("valid_input")
    assert result == "expected_output"


def test_function_raises_on_invalid():
    with pytest.raises(ValueError):
        function_to_test(None)


@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
])
def test_function_parametrized(input, expected):
    assert function_to_test(input) == expected
""",
            setup_code="""
@pytest.fixture
def sample_data():
    return {"key": "value"}
""",
        )
        
        # Python - unittest
        self._templates["unittest"] = TestTemplate(
            framework="unittest",
            language="python",
            file_extension=".py",
            import_statement="import unittest",
            test_function_prefix="test_",
            assertion_style="assertEquals",
            instructions="""
Generate unittest-style tests:
- Create a class inheriting from unittest.TestCase
- Use 'def test_method_name(self)' naming
- Use self.assertEqual, self.assertTrue, etc.
- Use setUp() and tearDown() for fixtures
- Use self.assertRaises for exception testing
""",
            example="""
import unittest
from module import function_to_test


class TestFunction(unittest.TestCase):
    def setUp(self):
        self.data = {"key": "value"}
    
    def test_success(self):
        result = function_to_test("valid")
        self.assertEqual(result, "expected")
    
    def test_raises_on_invalid(self):
        with self.assertRaises(ValueError):
            function_to_test(None)


if __name__ == "__main__":
    unittest.main()
""",
        )
        
        # JavaScript - Jest
        self._templates["jest"] = TestTemplate(
            framework="jest",
            language="javascript",
            file_extension=".js",
            import_statement="const { functionToTest } = require('./module');",
            test_function_prefix="",
            assertion_style="expect",
            instructions="""
Generate Jest-style tests:
- Use describe() for grouping
- Use it() or test() for individual tests
- Use expect().toBe() style assertions
- Use beforeEach/afterEach for setup/teardown
- Use jest.mock() for mocking
""",
            example="""
const { functionToTest } = require('./module');

describe('functionToTest', () => {
  beforeEach(() => {
    // Setup
  });

  it('should return expected output for valid input', () => {
    const result = functionToTest('valid');
    expect(result).toBe('expected');
  });

  it('should throw on invalid input', () => {
    expect(() => functionToTest(null)).toThrow();
  });

  it.each([
    ['a', 1],
    ['b', 2],
  ])('should handle %s correctly', (input, expected) => {
    expect(functionToTest(input)).toBe(expected);
  });
});
""",
        )
        
        # TypeScript - Vitest
        self._templates["vitest"] = TestTemplate(
            framework="vitest",
            language="typescript",
            file_extension=".ts",
            import_statement="import { describe, it, expect, beforeEach, vi } from 'vitest';",
            test_function_prefix="",
            assertion_style="expect",
            instructions="""
Generate Vitest-style tests:
- Use describe() for grouping
- Use it() or test() for individual tests
- Use expect().toBe() style assertions
- Use beforeEach/afterEach for setup/teardown
- Use vi.mock() for mocking
- Include TypeScript types
""",
            example="""
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { functionToTest } from './module';

describe('functionToTest', () => {
  beforeEach(() => {
    // Setup
  });

  it('should return expected output for valid input', () => {
    const result = functionToTest('valid');
    expect(result).toBe('expected');
  });

  it('should throw on invalid input', () => {
    expect(() => functionToTest(null)).toThrow();
  });
});
""",
        )
        
        # JavaScript - Mocha
        self._templates["mocha"] = TestTemplate(
            framework="mocha",
            language="javascript",
            file_extension=".js",
            import_statement="const { expect } = require('chai');\nconst { functionToTest } = require('./module');",
            test_function_prefix="",
            assertion_style="expect",
            instructions="""
Generate Mocha-style tests with Chai assertions:
- Use describe() for grouping
- Use it() for individual tests
- Use Chai expect().to style assertions
- Use before/after for setup/teardown
""",
            example="""
const { expect } = require('chai');
const { functionToTest } = require('./module');

describe('functionToTest', () => {
  it('should return expected output', () => {
    const result = functionToTest('valid');
    expect(result).to.equal('expected');
  });

  it('should throw on invalid input', () => {
    expect(() => functionToTest(null)).to.throw();
  });
});
""",
        )
        
        # Go - testing
        self._templates["testing"] = TestTemplate(
            framework="testing",
            language="go",
            file_extension="_test.go",
            import_statement='import "testing"',
            test_function_prefix="Test",
            assertion_style="t.Error",
            instructions="""
Generate Go testing-style tests:
- Use func TestXxx(t *testing.T) naming
- Use t.Error, t.Fatal for assertions
- Use t.Run for subtests
- Use t.Parallel() for parallel tests
""",
            example="""
package module

import "testing"

func TestFunctionToTest(t *testing.T) {
    result := FunctionToTest("valid")
    if result != "expected" {
        t.Errorf("got %v, want %v", result, "expected")
    }
}

func TestFunctionToTestSubtests(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected string
    }{
        {"case1", "a", "1"},
        {"case2", "b", "2"},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := FunctionToTest(tt.input)
            if result != tt.expected {
                t.Errorf("got %v, want %v", result, tt.expected)
            }
        })
    }
}
""",
        )
    
    def get_template(self, framework: str) -> Optional[TestTemplate]:
        """Get template for a framework.
        
        Args:
            framework: Test framework name
            
        Returns:
            Template or None if not found
        """
        return self._templates.get(framework)
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of available frameworks."""
        return list(self._templates.keys())
    
    def get_framework_for_language(self, language: str) -> Optional[str]:
        """Get default framework for a language."""
        defaults = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "vitest",
            "go": "testing",
        }
        return defaults.get(language)
    
    def add_template(self, template: TestTemplate) -> None:
        """Add a custom template."""
        self._templates[template.framework] = template
