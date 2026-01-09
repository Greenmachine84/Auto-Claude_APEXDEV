"""Dependency mapper for project analysis.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

import ast
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DependencyGraph:
    """Dependency graph representation."""

    nodes: set[str] = field(default_factory=set)
    edges: list[tuple[str, str]] = field(default_factory=list)  # (from, to)
    external_deps: list[str] = field(default_factory=list)
    internal_deps: list[tuple[str, str]] = field(default_factory=list)
    circular_deps: list[list[str]] = field(default_factory=list)
    orphan_files: list[str] = field(default_factory=list)
    hub_files: list[dict[str, Any]] = field(default_factory=list)

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node)

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge to the graph."""
        self.edges.append((from_node, to_node))
        self.add_node(from_node)
        self.add_node(to_node)

    def get_dependencies(self, node: str) -> list[str]:
        """Get all dependencies of a node."""
        return [to_node for from_node, to_node in self.edges if from_node == node]

    def get_dependents(self, node: str) -> list[str]:
        """Get all nodes that depend on this node."""
        return [from_node for from_node, to_node in self.edges if to_node == node]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": list(self.nodes),
            "edges": self.edges,
            "external_deps": self.external_deps,
            "internal_deps": self.internal_deps,
            "circular_deps": self.circular_deps,
            "orphan_files": self.orphan_files,
            "hub_files": self.hub_files,
        }


class DependencyMapper:
    """Maps dependencies between files in a project.

    Analyzes import statements and module references
    to build a dependency graph.
    """

    # Standard library modules (partial list)
    STDLIB_MODULES = {
        "os",
        "sys",
        "re",
        "json",
        "logging",
        "typing",
        "pathlib",
        "collections",
        "itertools",
        "functools",
        "datetime",
        "time",
        "asyncio",
        "threading",
        "multiprocessing",
        "subprocess",
        "unittest",
        "pytest",
        "abc",
        "dataclasses",
        "enum",
        "io",
        "http",
        "urllib",
        "socket",
        "ssl",
        "hashlib",
        "copy",
        "pickle",
        "shelve",
        "sqlite3",
        "csv",
        "xml",
    }

    def __init__(self):
        """Initialize mapper."""
        self._graph: DependencyGraph | None = None

    def build_graph(
        self,
        files: dict[str, str],
    ) -> DependencyGraph:
        """Build dependency graph from files.

        Args:
            files: Map of file paths to contents

        Returns:
            Dependency graph
        """
        graph = DependencyGraph()

        # Add all files as nodes
        for file_path in files:
            graph.add_node(file_path)

        # Analyze each file
        for file_path, content in files.items():
            if file_path.endswith(".py"):
                imports = self._extract_python_imports(content)
            elif file_path.endswith((".js", ".ts", ".tsx")):
                imports = self._extract_js_imports(content)
            else:
                continue

            for imp in imports:
                if self._is_external(imp):
                    if imp not in graph.external_deps:
                        graph.external_deps.append(imp)
                else:
                    # Try to resolve to internal file
                    resolved = self._resolve_internal(imp, file_path, files)
                    if resolved:
                        graph.add_edge(file_path, resolved)
                        graph.internal_deps.append((file_path, resolved))

        # Find circular dependencies
        graph.circular_deps = self._find_circular_deps(graph)

        # Find orphan files (no dependencies, no dependents)
        for node in graph.nodes:
            deps = graph.get_dependencies(node)
            dependents = graph.get_dependents(node)
            if not deps and not dependents:
                graph.orphan_files.append(node)

        # Find hub files (many dependents)
        dep_counts: dict[str, int] = {}
        for _, to_node in graph.edges:
            dep_counts[to_node] = dep_counts.get(to_node, 0) + 1

        for node, count in sorted(dep_counts.items(), key=lambda x: -x[1])[:10]:
            if count >= 3:
                graph.hub_files.append({"file": node, "dependents": count})

        self._graph = graph
        return graph

    def _extract_python_imports(
        self,
        code: str,
    ) -> list[str]:
        """Extract imports from Python code."""
        imports: list[str] = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])
        except SyntaxError:
            # Fallback to regex
            pattern = r"^(?:from|import)\s+([\w.]+)"
            for match in re.finditer(pattern, code, re.MULTILINE):
                imports.append(match.group(1).split(".")[0])

        return imports

    def _extract_js_imports(
        self,
        code: str,
    ) -> list[str]:
        """Extract imports from JavaScript/TypeScript code."""
        imports: list[str] = []

        # import ... from '...'
        pattern1 = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
        # require('...')
        pattern2 = r"require\(['\"]([^'\"]+)['\"]\)"

        for pattern in [pattern1, pattern2]:
            for match in re.finditer(pattern, code):
                imports.append(match.group(1))

        return imports

    def _is_external(self, module: str) -> bool:
        """Check if module is external."""
        # Python stdlib
        if module in self.STDLIB_MODULES:
            return True

        # Relative imports are internal
        if module.startswith("."):
            return False

        # Node modules pattern
        if not module.startswith(".") and not module.startswith("/"):
            # Could be npm package
            if module.startswith("@") or "/" not in module:
                return True

        return True  # Default to external for unknown

    def _resolve_internal(
        self,
        module: str,
        from_file: str,
        files: dict[str, str],
    ) -> str | None:
        """Resolve module to internal file path."""
        # Handle relative imports
        if module.startswith("."):
            import os

            base_dir = os.path.dirname(from_file)

            if module.startswith(".."):
                # Go up one directory
                base_dir = os.path.dirname(base_dir)
                module = module[2:]
            else:
                module = module[1:]

            # Try to find matching file
            for ext in [
                ".py",
                ".js",
                ".ts",
                ".tsx",
                "/index.py",
                "/index.js",
                "/index.ts",
            ]:
                candidate = os.path.join(base_dir, module + ext)
                candidate = candidate.replace("\\", "/")  # Normalize path
                if candidate in files:
                    return candidate

        # Try direct match
        for ext in [".py", ".js", ".ts"]:
            candidate = module.replace(".", "/") + ext
            if candidate in files:
                return candidate

        return None

    def _find_circular_deps(
        self,
        graph: DependencyGraph,
    ) -> list[list[str]]:
        """Find circular dependencies in graph."""
        circular: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in graph.get_dependencies(node):
                if dep not in visited:
                    dfs(dep)
                elif dep in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    if cycle not in circular:
                        circular.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph.nodes:
            if node not in visited:
                dfs(node)

        return circular

    def get_import_suggestions(
        self,
        graph: DependencyGraph,
    ) -> list[str]:
        """Get suggestions for improving imports."""
        suggestions: list[str] = []

        if graph.circular_deps:
            suggestions.append(
                f"Found {len(graph.circular_deps)} circular dependencies. "
                "Consider refactoring to break these cycles."
            )

        if len(graph.hub_files) > 0:
            suggestions.append(
                f"Found {len(graph.hub_files)} hub files with many dependents. "
                "Consider splitting these modules."
            )

        if len(graph.orphan_files) > 0:
            suggestions.append(
                f"Found {len(graph.orphan_files)} orphan files. "
                "These may be unused or dead code."
            )

        return suggestions
