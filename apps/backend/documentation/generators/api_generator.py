"""
API documentation generator.

Generates API documentation from Python source code,
including classes, functions, and endpoints.
"""

import ast
import inspect
from pathlib import Path
from typing import Any

from ..config import DocumentationConfig
from ..models import (
    ApiEndpoint,
    DocumentationEntry,
    Visibility,
)
from .base import BaseGenerator


class ApiDocGenerator(BaseGenerator):
    """Generates API documentation from source code."""

    def __init__(self, config: DocumentationConfig):
        """Initialize API documentation generator."""
        super().__init__(config)
        self.current_module: str | None = None

    def generate(self, source: Any) -> list[DocumentationEntry]:
        """
        Generate API documentation from source.

        Args:
            source: Python module, class, or function

        Returns:
            List of documentation entries
        """
        entries = []

        if inspect.ismodule(source):
            entries.extend(self._document_module(source))
        elif inspect.isclass(source):
            entries.append(self._document_class(source))
        elif inspect.isfunction(source) or inspect.ismethod(source):
            entries.append(self._document_function(source))

        return entries

    def generate_from_file(self, file_path: Path) -> list[DocumentationEntry]:
        """
        Generate API documentation from a Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            List of documentation entries
        """
        entries = []

        if not file_path.suffix == ".py":
            return entries

        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self.current_module = self._get_module_name(file_path)

            # Process module docstring
            module_doc = ast.get_docstring(tree)
            if module_doc:
                entries.append(
                    self._create_module_entry(
                        self.current_module, module_doc, file_path
                    )
                )

            # Process classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entry = self._process_class_node(node, file_path)
                    if entry:
                        entries.append(entry)
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if self._is_top_level(node, tree):
                        entry = self._process_function_node(node, file_path)
                        if entry:
                            entries.append(entry)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

        return entries

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        # Remove .py extension and convert path separators to dots
        relative = (
            file_path.relative_to(self.config.source_dirs[0])
            if self.config.source_dirs
            else file_path
        )
        return str(relative.with_suffix("")).replace("/", ".").replace("\\", ".")

    def _is_top_level(self, node: ast.AST, tree: ast.Module) -> bool:
        """Check if node is at module level."""
        return node in tree.body

    def _create_module_entry(
        self, name: str, docstring: str, source_file: Path
    ) -> DocumentationEntry:
        """Create documentation entry for a module."""
        return DocumentationEntry(
            id=self.get_entry_id(name),
            title=f"Module: {name}",
            content=docstring,
            entry_type="module",
            source_file=source_file,
            tags=["module", "api"],
        )

    def _process_class_node(
        self, node: ast.ClassDef, source_file: Path
    ) -> DocumentationEntry | None:
        """Process class AST node."""
        # Skip private classes unless configured
        if node.name.startswith("_") and not self.config.parser.include_private:
            return None

        docstring = ast.get_docstring(node) or ""
        visibility = (
            Visibility.PRIVATE if node.name.startswith("_") else Visibility.PUBLIC
        )

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._process_method_node(item, node.name)
                if method_doc:
                    methods.append(method_doc)

        # Build content
        content_parts = [docstring]
        if methods:
            content_parts.append("\n## Methods\n")
            for method in methods:
                content_parts.append(f"### `{method['name']}`\n")
                content_parts.append(method.get("docstring", "") + "\n")
                if method.get("signature"):
                    content_parts.append(f"```python\n{method['signature']}\n```\n")

        return DocumentationEntry(
            id=self.get_entry_id(node.name, self.current_module),
            title=f"Class: {node.name}",
            content="\n".join(content_parts),
            entry_type="class",
            visibility=visibility,
            source_file=source_file,
            source_line=node.lineno,
            tags=["class", "api"],
        )

    def _process_method_node(
        self, node: ast.FunctionDef, class_name: str
    ) -> dict | None:
        """Process method AST node."""
        # Skip dunder methods unless configured
        if node.name.startswith("__") and not self.config.parser.include_dunder:
            if node.name not in ("__init__", "__call__", "__enter__", "__exit__"):
                return None

        # Skip private methods unless configured
        if node.name.startswith("_") and not node.name.startswith("__"):
            if not self.config.parser.include_private:
                return None

        docstring = ast.get_docstring(node) or ""
        signature = self._get_function_signature(node)

        return {
            "name": node.name,
            "docstring": docstring,
            "signature": signature,
            "lineno": node.lineno,
        }

    def _process_function_node(
        self, node: ast.FunctionDef, source_file: Path
    ) -> DocumentationEntry | None:
        """Process function AST node."""
        # Skip private functions unless configured
        if node.name.startswith("_") and not self.config.parser.include_private:
            return None

        docstring = ast.get_docstring(node) or ""
        signature = self._get_function_signature(node)
        visibility = (
            Visibility.PRIVATE if node.name.startswith("_") else Visibility.PUBLIC
        )

        content = f"{docstring}\n\n```python\n{signature}\n```"

        return DocumentationEntry(
            id=self.get_entry_id(node.name, self.current_module),
            title=f"Function: {node.name}",
            content=content,
            entry_type="function",
            visibility=visibility,
            source_file=source_file,
            source_line=node.lineno,
            tags=["function", "api"],
        )

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature from AST node."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        # Return annotation
        returns = ""
        if node.returns:
            returns = f" -> {ast.unparse(node.returns)}"

        return f"def {node.name}({', '.join(args)}){returns}"

    def _document_module(self, module: Any) -> list[DocumentationEntry]:
        """Document a Python module."""
        entries = []

        doc = inspect.getdoc(module) or ""
        module_name = module.__name__

        entries.append(
            DocumentationEntry(
                id=self.get_entry_id(module_name),
                title=f"Module: {module_name}",
                content=doc,
                entry_type="module",
                tags=["module", "api"],
            )
        )

        # Document classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                entries.append(self._document_class(obj))

        # Document functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module_name:
                entries.append(self._document_function(obj))

        return entries

    def _document_class(self, cls: type) -> DocumentationEntry:
        """Document a Python class."""
        doc = inspect.getdoc(cls) or ""
        source_file = None
        source_line = None

        try:
            source_file = Path(inspect.getfile(cls))
            source_line = inspect.getsourcelines(cls)[1]
        except (TypeError, OSError):
            pass

        return DocumentationEntry(
            id=self.get_entry_id(cls.__name__, cls.__module__),
            title=f"Class: {cls.__name__}",
            content=doc,
            entry_type="class",
            source_file=source_file,
            source_line=source_line,
            tags=["class", "api"],
        )

    def _document_function(self, func: Any) -> DocumentationEntry:
        """Document a Python function."""
        doc = inspect.getdoc(func) or ""
        sig = str(inspect.signature(func))
        source_file = None
        source_line = None

        try:
            source_file = Path(inspect.getfile(func))
            source_line = inspect.getsourcelines(func)[1]
        except (TypeError, OSError):
            pass

        content = f"{doc}\n\n```python\ndef {func.__name__}{sig}\n```"

        return DocumentationEntry(
            id=self.get_entry_id(func.__name__, func.__module__),
            title=f"Function: {func.__name__}",
            content=content,
            entry_type="function",
            source_file=source_file,
            source_line=source_line,
            tags=["function", "api"],
        )

    def generate_endpoint_doc(self, endpoint: ApiEndpoint) -> DocumentationEntry:
        """
        Generate documentation for an API endpoint.

        Args:
            endpoint: API endpoint definition

        Returns:
            Documentation entry for the endpoint
        """
        return DocumentationEntry(
            id=endpoint.id,
            title=f"{endpoint.method.value} {endpoint.path}",
            content=endpoint.to_markdown(),
            entry_type="endpoint",
            tags=["api", "endpoint"] + endpoint.tags,
            examples=endpoint.examples,
        )
