"""Docstring generator for documentation agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GeneratedDocstring:
    """A generated docstring."""

    function_name: str
    docstring: str
    style: str = "google"
    params: list[dict[str, str]] = field(default_factory=list)
    returns: str | None = None
    raises: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def to_string(self) -> str:
        """Convert to docstring string."""
        return f'"""\n{self.docstring}\n"""'


class DocstringGenerator:
    """Generates docstrings from code analysis.

    Analyzes function signatures and generates
    appropriate docstrings in various styles.
    """

    def __init__(self, default_style: str = "google"):
        """Initialize generator."""
        self.default_style = default_style

    def analyze_function(
        self,
        code: str,
        language: str = "python",
    ) -> list[dict[str, Any]]:
        """Analyze functions in code.

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of function info dicts
        """
        functions: list[dict[str, Any]] = []

        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_info = self._analyze_python_function(node)
                        functions.append(func_info)
            except SyntaxError:
                pass

        return functions

    def _analyze_python_function(
        self,
        node: ast.FunctionDef,
    ) -> dict[str, Any]:
        """Analyze a Python function AST node."""
        params: list[dict[str, str]] = []

        # Get parameters
        for arg in node.args.args:
            param = {
                "name": arg.arg,
                "type": "",
            }
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            params.append(param)

        # Get return type
        return_type = ""
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Check for existing docstring
        existing_doc = ast.get_docstring(node) or ""

        return {
            "name": node.name,
            "params": params,
            "return_type": return_type,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "has_docstring": bool(existing_doc),
            "existing_docstring": existing_doc,
            "lineno": node.lineno,
        }

    def generate_google_style(
        self,
        func_info: dict[str, Any],
    ) -> str:
        """Generate Google-style docstring."""
        lines = ['"""[Summary].', ""]

        # Add args section
        if func_info.get("params"):
            lines.append("Args:")
            for param in func_info["params"]:
                if param["name"] == "self":
                    continue
                type_str = f" ({param['type']})" if param["type"] else ""
                lines.append(f"    {param['name']}{type_str}: [Description].")
            lines.append("")

        # Add returns section
        if func_info.get("return_type") and func_info["return_type"] != "None":
            lines.append("Returns:")
            lines.append(f"    {func_info['return_type']}: [Description].")
            lines.append("")

        lines.append('"""')
        return "\n".join(lines)

    def generate_numpy_style(
        self,
        func_info: dict[str, Any],
    ) -> str:
        """Generate NumPy-style docstring."""
        lines = ['"""[Summary].', ""]

        # Add parameters section
        if func_info.get("params"):
            lines.append("Parameters")
            lines.append("----------")
            for param in func_info["params"]:
                if param["name"] == "self":
                    continue
                type_str = param["type"] if param["type"] else "type"
                lines.append(f"{param['name']} : {type_str}")
                lines.append("    [Description].")
            lines.append("")

        # Add returns section
        if func_info.get("return_type") and func_info["return_type"] != "None":
            lines.append("Returns")
            lines.append("-------")
            lines.append(func_info["return_type"])
            lines.append("    [Description].")
            lines.append("")

        lines.append('"""')
        return "\n".join(lines)

    def generate_sphinx_style(
        self,
        func_info: dict[str, Any],
    ) -> str:
        """Generate Sphinx-style docstring."""
        lines = ['"""[Summary].', ""]

        # Add parameters
        for param in func_info.get("params", []):
            if param["name"] == "self":
                continue
            lines.append(f":param {param['name']}: [Description].")
            if param["type"]:
                lines.append(f":type {param['name']}: {param['type']}")

        # Add returns
        if func_info.get("return_type") and func_info["return_type"] != "None":
            lines.append(":returns: [Description].")
            lines.append(f":rtype: {func_info['return_type']}")

        lines.append("")
        lines.append('"""')
        return "\n".join(lines)

    def generate_docstring(
        self,
        func_info: dict[str, Any],
        style: str = "google",
    ) -> str:
        """Generate docstring in specified style.

        Args:
            func_info: Function info from analyze_function
            style: Docstring style (google, numpy, sphinx)

        Returns:
            Generated docstring
        """
        if style == "numpy":
            return self.generate_numpy_style(func_info)
        elif style == "sphinx":
            return self.generate_sphinx_style(func_info)
        else:
            return self.generate_google_style(func_info)

    def insert_docstrings(
        self,
        code: str,
        docstrings: dict[str, str],
    ) -> str:
        """Insert docstrings into code.

        Args:
            code: Original source code
            docstrings: Map of function name to docstring

        Returns:
            Code with docstrings inserted
        """
        # This is a simplified implementation
        # In production, use AST transformation
        lines = code.split("\n")
        result_lines: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            result_lines.append(line)

            # Check if this is a function definition
            match = re.match(r"^(\s*)(?:async\s+)?def\s+(\w+)", line)
            if match:
                indent = match.group(1)
                func_name = match.group(2)

                if func_name in docstrings:
                    # Check if next line is already a docstring
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if not (
                            next_line.startswith('"""') or next_line.startswith("'''")
                        ):
                            # Insert docstring
                            docstring = docstrings[func_name]
                            for doc_line in docstring.split("\n"):
                                result_lines.append(f"{indent}    {doc_line}")

            i += 1

        return "\n".join(result_lines)
