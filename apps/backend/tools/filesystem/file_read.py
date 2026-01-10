"""File read tool.

Reads file contents.

Capabilities:
- Read entire files
- Read file ranges
- Handle binary files
- Detect encoding
"""

import os

import chardet
from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class FileReadTool(BaseTool):
    """Read file contents.

    Reads files with support for line ranges and
    automatic encoding detection.

    Example:
        tool = FileReadTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/file.txt",
                "start_line": 1,
                "end_line": 100,
            }
        ))
    """

    name = "file_read"
    description = "Read contents of a file"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"read_files"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Path to file to read",
                required=True,
            ),
            ToolParameter(
                name="start_line",
                type="integer",
                description="Starting line number (1-indexed)",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="end_line",
                type="integer",
                description="Ending line number (inclusive)",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding (auto-detected if not specified)",
                required=False,
                default=None,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute file read.

        Args:
            context: Execution context with path

        Returns:
            ToolResult with file contents
        """
        path = context.parameters.get("path")
        start_line = context.parameters.get("start_line")
        end_line = context.parameters.get("end_line")
        encoding = context.parameters.get("encoding")

        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        # Check file exists
        if not os.path.exists(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"File not found: {path}",
            )

        if not os.path.isfile(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Not a file: {path}",
            )

        try:
            # Detect encoding if not specified
            if not encoding:
                encoding = self._detect_encoding(path)

            # Read file
            with open(path, encoding=encoding) as f:
                if start_line or end_line:
                    lines = f.readlines()
                    start = (start_line or 1) - 1
                    end = end_line or len(lines)
                    content = "".join(lines[start:end])
                    total_lines = len(lines)
                else:
                    content = f.read()
                    total_lines = content.count("\n") + 1

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "content": content,
                    "path": path,
                    "encoding": encoding,
                    "total_lines": total_lines,
                    "start_line": start_line or 1,
                    "end_line": end_line or total_lines,
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )

    def _detect_encoding(self, path: str) -> str:
        """Detect file encoding."""
        try:
            with open(path, "rb") as f:
                raw = f.read(10000)
            result = chardet.detect(raw)
            return result.get("encoding", "utf-8") or "utf-8"
        except Exception:
            return "utf-8"
