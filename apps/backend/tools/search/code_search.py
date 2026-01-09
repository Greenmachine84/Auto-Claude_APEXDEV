"""Code search tool.

Searches for code patterns.

Capabilities:
- Search by symbol
- Search by pattern
- Filter by language
- Find definitions
"""

import os
import re

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class CodeSearchTool(BaseTool):
    """Search for code patterns.

    Example:
        tool = CodeSearchTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/repo",
                "query": "def process_",
            }
        ))
    """

    name = "code_search"
    description = "Search for code patterns"
    category = ToolCategory.SEARCH
    required_permissions = {"read_files"}
    version = "1.0.0"

    # Language file extensions
    EXTENSIONS = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "java": [".java"],
        "go": [".go"],
        "rust": [".rs"],
        "ruby": [".rb"],
        "csharp": [".cs"],
    }

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Directory to search in",
                required=True,
            ),
            ToolParameter(
                name="query",
                type="string",
                description="Search query (text or regex)",
                required=True,
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Filter by language",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="regex",
                type="boolean",
                description="Treat query as regex",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum results",
                required=False,
                default=50,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute code search."""
        path = context.parameters.get("path")
        query = context.parameters.get("query")
        language = context.parameters.get("language")
        use_regex = context.parameters.get("regex", False)
        max_results = context.parameters.get("max_results", 50)

        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        try:
            # Get file extensions to search
            extensions = None
            if language and language in self.EXTENSIONS:
                extensions = self.EXTENSIONS[language]

            # Search files
            results = []
            for root, dirs, files in os.walk(path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for name in files:
                    if len(results) >= max_results:
                        break

                    # Check extension
                    if extensions:
                        if not any(name.endswith(ext) for ext in extensions):
                            continue

                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, path)

                    matches = self._search_file(full_path, query, use_regex)
                    if matches:
                        results.append(
                            {
                                "file": rel_path,
                                "matches": matches[:5],
                            }
                        )

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "results": results,
                    "count": len(results),
                    "query": query,
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )

    def _search_file(self, path: str, query: str, use_regex: bool) -> list[dict]:
        """Search a single file."""
        matches = []

        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if use_regex:
                        if re.search(query, line):
                            matches.append({"line": i, "text": line.strip()[:200]})
                    else:
                        if query in line:
                            matches.append({"line": i, "text": line.strip()[:200]})
        except Exception:
            pass

        return matches
