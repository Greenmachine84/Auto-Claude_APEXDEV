"""
Search Tools - Phase 8 Builtin.

Consolidated search operations.
"""

import logging
import re
from pathlib import Path

from ..models import (
    ParameterType,
    Tool,
    ToolCategory,
    ToolExecutionContext,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class SearchTools:
    """Search operation tools."""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Get all search tools."""
        return [
            SearchTools._grep_tool(),
            SearchTools._find_files_tool(),
            SearchTools._search_code_tool(),
        ]

    @staticmethod
    def _grep_tool() -> Tool:
        return Tool(
            name="grep",
            description="Search for pattern in files",
            category=ToolCategory.SEARCH,
            parameters=[
                ToolParameter(
                    name="pattern",
                    type=ParameterType.STRING,
                    description="Search pattern",
                    required=True,
                ),
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="Search path",
                    default=".",
                ),
                ToolParameter(
                    name="regex",
                    type=ParameterType.BOOLEAN,
                    description="Use regex",
                    default=False,
                ),
            ],
            handler=SearchTools.grep,
            tags=["search", "grep"],
        )

    @staticmethod
    def _find_files_tool() -> Tool:
        return Tool(
            name="find_files",
            description="Find files by pattern",
            category=ToolCategory.SEARCH,
            parameters=[
                ToolParameter(
                    name="pattern",
                    type=ParameterType.STRING,
                    description="Glob pattern",
                    required=True,
                ),
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="Search path",
                    default=".",
                ),
            ],
            handler=SearchTools.find_files,
            tags=["search", "find"],
        )

    @staticmethod
    def _search_code_tool() -> Tool:
        return Tool(
            name="search_code",
            description="Search code for symbol",
            category=ToolCategory.SEARCH,
            parameters=[
                ToolParameter(
                    name="symbol",
                    type=ParameterType.STRING,
                    description="Symbol name",
                    required=True,
                ),
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="Search path",
                    default=".",
                ),
                ToolParameter(
                    name="extensions",
                    type=ParameterType.ARRAY,
                    description="File extensions",
                    default=[".py", ".ts", ".js"],
                ),
            ],
            handler=SearchTools.search_code,
            tags=["search", "code"],
        )

    @staticmethod
    async def grep(
        ctx: ToolExecutionContext, pattern: str, path: str = ".", regex: bool = False
    ) -> ToolResult:
        """Search for pattern in files."""
        try:
            matches = []
            p = Path(path)
            search_re = re.compile(pattern) if regex else None

            for file in p.rglob("*"):
                if not file.is_file():
                    continue
                try:
                    content = file.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if (search_re and search_re.search(line)) or (
                            not regex and pattern in line
                        ):
                            matches.append(
                                {
                                    "file": str(file),
                                    "line": i,
                                    "text": line.strip()[:200],
                                }
                            )
                except Exception:
                    continue

            return ToolResult(
                output=matches,
                error=None,
                metadata={"pattern": pattern, "count": len(matches)},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"pattern": pattern})

    @staticmethod
    async def find_files(
        ctx: ToolExecutionContext, pattern: str, path: str = "."
    ) -> ToolResult:
        """Find files by glob pattern."""
        try:
            files = [str(f) for f in Path(path).rglob(pattern)]
            return ToolResult(
                output=files,
                error=None,
                metadata={"pattern": pattern, "count": len(files)},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"pattern": pattern})

    @staticmethod
    async def search_code(
        ctx: ToolExecutionContext,
        symbol: str,
        path: str = ".",
        extensions: list[str] = None,
    ) -> ToolResult:
        """Search for code symbol."""
        extensions = extensions or [".py", ".ts", ".js"]
        try:
            matches = []
            p = Path(path)

            for ext in extensions:
                for file in p.rglob(f"*{ext}"):
                    try:
                        content = file.read_text(errors="ignore")
                        for i, line in enumerate(content.split("\n"), 1):
                            if symbol in line:
                                matches.append(
                                    {
                                        "file": str(file),
                                        "line": i,
                                        "text": line.strip()[:200],
                                    }
                                )
                    except Exception:
                        continue

            return ToolResult(
                output=matches,
                error=None,
                metadata={"symbol": symbol, "count": len(matches)},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"symbol": symbol})
