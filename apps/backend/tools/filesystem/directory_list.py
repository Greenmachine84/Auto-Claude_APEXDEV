"""Directory list tool.

Lists directory contents.

Capabilities:
- List files and subdirectories
- Recursive listing
- Filter by pattern
- Include file metadata
"""

import fnmatch
import os
from datetime import datetime
from typing import Any

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class DirectoryListTool(BaseTool):
    """List directory contents.

    Lists files and directories with optional filtering
    and metadata.

    Example:
        tool = DirectoryListTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/dir",
                "pattern": "*.py",
            }
        ))
    """

    name = "directory_list"
    description = "List directory contents"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"read_files"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Directory path to list",
                required=True,
            ),
            ToolParameter(
                name="pattern",
                type="string",
                description="Glob pattern to filter files",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="recursive",
                type="boolean",
                description="List recursively",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="include_hidden",
                type="boolean",
                description="Include hidden files",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="include_metadata",
                type="boolean",
                description="Include file metadata",
                required=False,
                default=False,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute directory listing.

        Args:
            context: Execution context with path

        Returns:
            ToolResult with directory contents
        """
        path = context.parameters.get("path")
        pattern = context.parameters.get("pattern")
        recursive = context.parameters.get("recursive", False)
        include_hidden = context.parameters.get("include_hidden", False)
        include_metadata = context.parameters.get("include_metadata", False)

        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        # Check exists
        if not os.path.exists(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Directory not found: {path}",
            )

        if not os.path.isdir(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Not a directory: {path}",
            )

        try:
            entries = []

            if recursive:
                for root, dirs, files in os.walk(path):
                    # Filter hidden
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]
                        files = [f for f in files if not f.startswith(".")]

                    for name in dirs + files:
                        full_path = os.path.join(root, name)
                        rel_path = os.path.relpath(full_path, path)

                        if pattern and not fnmatch.fnmatch(name, pattern):
                            continue

                        entry = self._create_entry(
                            full_path, rel_path, include_metadata
                        )
                        entries.append(entry)
            else:
                for name in os.listdir(path):
                    if not include_hidden and name.startswith("."):
                        continue

                    if pattern and not fnmatch.fnmatch(name, pattern):
                        continue

                    full_path = os.path.join(path, name)
                    entry = self._create_entry(full_path, name, include_metadata)
                    entries.append(entry)

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "path": path,
                    "entries": entries,
                    "count": len(entries),
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )

    def _create_entry(
        self,
        full_path: str,
        rel_path: str,
        include_metadata: bool,
    ) -> dict[str, Any]:
        """Create directory entry."""
        is_dir = os.path.isdir(full_path)

        entry = {
            "name": rel_path,
            "type": "directory" if is_dir else "file",
        }

        if include_metadata and not is_dir:
            stat = os.stat(full_path)
            entry["size"] = stat.st_size
            entry["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return entry
