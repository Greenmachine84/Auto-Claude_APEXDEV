"""
File Tools - Phase 8 Builtin.

Consolidated file operations.
"""

import logging
import os
from pathlib import Path

import aiofiles

from ..models import (
    ParameterType,
    Tool,
    ToolCategory,
    ToolExecutionContext,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class FileTools:
    """File operation tools."""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Get all file tools."""
        return [
            FileTools._read_file_tool(),
            FileTools._write_file_tool(),
            FileTools._list_dir_tool(),
            FileTools._delete_file_tool(),
        ]

    @staticmethod
    def _read_file_tool() -> Tool:
        return Tool(
            name="read_file",
            description="Read contents of a file",
            category=ToolCategory.FILE_SYSTEM,
            parameters=[
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="File path",
                    required=True,
                ),
                ToolParameter(
                    name="encoding",
                    type=ParameterType.STRING,
                    description="Encoding",
                    default="utf-8",
                ),
            ],
            handler=FileTools.read_file,
            tags=["file", "read"],
        )

    @staticmethod
    def _write_file_tool() -> Tool:
        return Tool(
            name="write_file",
            description="Write content to a file",
            category=ToolCategory.FILE_SYSTEM,
            parameters=[
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="File path",
                    required=True,
                ),
                ToolParameter(
                    name="content",
                    type=ParameterType.STRING,
                    description="Content",
                    required=True,
                ),
                ToolParameter(
                    name="encoding",
                    type=ParameterType.STRING,
                    description="Encoding",
                    default="utf-8",
                ),
            ],
            handler=FileTools.write_file,
            requires_confirmation=True,
            tags=["file", "write"],
        )

    @staticmethod
    def _list_dir_tool() -> Tool:
        return Tool(
            name="list_directory",
            description="List directory contents",
            category=ToolCategory.FILE_SYSTEM,
            parameters=[
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="Directory path",
                    required=True,
                ),
                ToolParameter(
                    name="recursive",
                    type=ParameterType.BOOLEAN,
                    description="Recursive",
                    default=False,
                ),
            ],
            handler=FileTools.list_directory,
            tags=["file", "directory", "list"],
        )

    @staticmethod
    def _delete_file_tool() -> Tool:
        return Tool(
            name="delete_file",
            description="Delete a file",
            category=ToolCategory.FILE_SYSTEM,
            parameters=[
                ToolParameter(
                    name="path",
                    type=ParameterType.FILE_PATH,
                    description="File path",
                    required=True,
                ),
            ],
            handler=FileTools.delete_file,
            requires_confirmation=True,
            tags=["file", "delete"],
        )

    @staticmethod
    async def read_file(
        ctx: ToolExecutionContext, path: str, encoding: str = "utf-8"
    ) -> ToolResult:
        """Read file contents."""
        try:
            async with aiofiles.open(path, encoding=encoding) as f:
                content = await f.read()
            return ToolResult(
                output=content,
                error=None,
                metadata={"path": path, "size": len(content)},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"path": path})

    @staticmethod
    async def write_file(
        ctx: ToolExecutionContext, path: str, content: str, encoding: str = "utf-8"
    ) -> ToolResult:
        """Write file contents."""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "w", encoding=encoding) as f:
                await f.write(content)
            return ToolResult(
                output={"written": len(content)}, error=None, metadata={"path": path}
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"path": path})

    @staticmethod
    async def list_directory(
        ctx: ToolExecutionContext, path: str, recursive: bool = False
    ) -> ToolResult:
        """List directory contents."""
        try:
            p = Path(path)
            if recursive:
                entries = [{"path": str(e), "is_dir": e.is_dir()} for e in p.rglob("*")]
            else:
                entries = [{"name": e.name, "is_dir": e.is_dir()} for e in p.iterdir()]
            return ToolResult(
                output=entries,
                error=None,
                metadata={"path": path, "count": len(entries)},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"path": path})

    @staticmethod
    async def delete_file(ctx: ToolExecutionContext, path: str) -> ToolResult:
        """Delete a file."""
        try:
            os.remove(path)
            return ToolResult(
                output={"deleted": path}, error=None, metadata={"path": path}
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"path": path})
