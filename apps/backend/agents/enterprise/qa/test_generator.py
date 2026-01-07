"""Test generator for QA agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import ast
import re


@dataclass
class GeneratedTest:
    """A generated test case."""
    name: str
    code: str
    target_function: str
    test_type: str = "unit"  # unit, integration, e2e
    framework: str = "pytest"
    assertions: List[str] = field(default_factory=list)
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    mocks: List[str] = field(default_factory=list)
    is_edge_case: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "code": self.code,
            "target_function": self.target_function,
            "test_type": self.test_type,
            "framework": self.framework,
            "assertions": self.assertions,
            "setup_code": self.setup_code,
            "teardown_code": self.teardown_code,
            "mocks": self.mocks,
            "is_edge_case": self.is_edge_case,
        }


class TestGenerator:
    """Generates test code from source code.
    
    Provides utilities for analyzing source code and
    generating appropriate test structures.
    """
    
    def __init__(self):
        """Initialize the test generator."""
        self._function_patterns = {
            "python": r"def\s+(\w+)\s*\(",
            "javascript": r"(function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?(?:function|\()|\w+\s*:\s*(?:async\s+)?function)",
            "typescript": r"(function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?(?:function|\()|\w+\s*:\s*(?:async\s+)?function)",
        }
    
    def extract_functions(self, code: str, language: str) -> List[str]:
        """Extract function names from source code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of function names
        """
        functions: List[str] = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not node.name.startswith("_"):  # Skip private
                            functions.append(node.name)
            except SyntaxError:
                # Fallback to regex
                pattern = self._function_patterns.get(language, "")
                if pattern:
                    matches = re.findall(pattern, code)
                    functions = [m for m in matches if not m.startswith("_")]
        else:
            pattern = self._function_patterns.get(language, "")
            if pattern:
                matches = re.findall(pattern, code)
                functions = matches
        
        return functions
    
    def extract_classes(self, code: str, language: str) -> List[str]:
        """Extract class names from source code."""
        classes: List[str] = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)
            except SyntaxError:
                pattern = r"class\s+(\w+)"
                classes = re.findall(pattern, code)
        else:
            pattern = r"class\s+(\w+)"
            classes = re.findall(pattern, code)
        
        return classes
    
    def generate_unit_tests(
        self,
        code: str,
        language: str,
        framework: str,
    ) -> str:
        """Generate unit test skeleton.
        
        Args:
            code: Source code
            language: Programming language
            framework: Test framework
            
        Returns:
            Test code skeleton
        """
        functions = self.extract_functions(code, language)
        classes = self.extract_classes(code, language)
        
        if framework == "pytest":
            return self._generate_pytest(functions, classes)
        elif framework in ("jest", "vitest"):
            return self._generate_jest(functions, classes)
        elif framework == "unittest":
            return self._generate_unittest(functions, classes)
        else:
            return self._generate_pytest(functions, classes)
    
    def _generate_pytest(self, functions: List[str], classes: List[str]) -> str:
        """Generate pytest test skeleton."""
        tests = ['"""Auto-generated tests."""', 'import pytest', '']
        
        for func in functions:
            tests.append(f'\ndef test_{func}_success():')
            tests.append(f'    """Test {func} with valid input."""')
            tests.append(f'    # TODO: Implement test for {func}')
            tests.append('    pass')
            tests.append('')
            tests.append(f'\ndef test_{func}_edge_case():')
            tests.append(f'    """Test {func} edge cases."""')
            tests.append('    # TODO: Add edge case tests')
            tests.append('    pass')
        
        for cls in classes:
            tests.append(f'\n\nclass Test{cls}:')
            tests.append(f'    """Tests for {cls} class."""')
            tests.append('')
            tests.append('    def test_init(self):')
            tests.append(f'        """Test {cls} initialization."""')
            tests.append('        pass')
        
        return '\n'.join(tests)
    
    def _generate_jest(self, functions: List[str], classes: List[str]) -> str:
        """Generate Jest/Vitest test skeleton."""
        tests = ['// Auto-generated tests', '']
        
        for func in functions:
            tests.append(f"describe('{func}', () => {{")
            tests.append(f"  it('should work with valid input', () => {{")
            tests.append(f'    // TODO: Implement test for {func}')
            tests.append('  });')
            tests.append('')
            tests.append(f"  it('should handle edge cases', () => {{")
            tests.append('    // TODO: Add edge case tests')
            tests.append('  });')
            tests.append('});')
            tests.append('')
        
        for cls in classes:
            tests.append(f"describe('{cls}', () => {{")
            tests.append(f"  it('should initialize correctly', () => {{")
            tests.append('    // TODO: Test initialization')
            tests.append('  });')
            tests.append('});')
            tests.append('')
        
        return '\n'.join(tests)
    
    def _generate_unittest(self, functions: List[str], classes: List[str]) -> str:
        """Generate unittest test skeleton."""
        tests = ['"""Auto-generated tests."""', 'import unittest', '']
        
        tests.append('class TestFunctions(unittest.TestCase):')
        tests.append('    """Test cases for functions."""')
        
        for func in functions:
            tests.append(f'')
            tests.append(f'    def test_{func}_success(self):')
            tests.append(f'        """Test {func} with valid input."""')
            tests.append('        pass')
        
        tests.append('')
        tests.append('')
        tests.append("if __name__ == '__main__':")
        tests.append('    unittest.main()')
        
        return '\n'.join(tests)
    
    def generate_edge_cases(
        self,
        function_code: str,
        language: str,
    ) -> List[str]:
        """Generate edge case descriptions for a function.
        
        Args:
            function_code: The function code to analyze
            language: Programming language
            
        Returns:
            List of edge case descriptions
        """
        edge_cases = [
            "Empty input",
            "Null/None input",
            "Very large input",
            "Negative numbers (if applicable)",
            "Unicode characters",
            "Concurrent access",
        ]
        
        # Analyze function for specific edge cases
        if "list" in function_code.lower() or "array" in function_code.lower():
            edge_cases.extend([
                "Empty array/list",
                "Single element array/list",
                "Very large array/list",
            ])
        
        if "string" in function_code.lower() or "str" in function_code.lower():
            edge_cases.extend([
                "Empty string",
                "Very long string",
                "Special characters",
            ])
        
        if "file" in function_code.lower():
            edge_cases.extend([
                "File not found",
                "Permission denied",
                "Empty file",
            ])
        
        return edge_cases
