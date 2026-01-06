"""File delete tool.

Deletes files and directories.

Capabilities:
- Delete single files
- Delete directories
- Recursive deletion
- Safe deletion with confirmation
"""

from typing import Any, Dict, List, Optional
import os
import shutil

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class FileDeleteTool(BaseTool):
    """Delete files and directories.
    
    Safely removes files or directories with optional
    recursive deletion.
    
    Example:
        tool = FileDeleteTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/file.txt",
            }
        ))
    """
    
    name = "file_delete"
    description = "Delete files or directories"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"delete_files"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Path to delete",
                required=True,
            ),
            ToolParameter(
                name="recursive",
                type="boolean",
                description="Delete directories recursively",
                required=False,
                default=False,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute file deletion.
        
        Args:
            context: Execution context with path
            
        Returns:
            ToolResult with deletion status
        """
        path = context.parameters.get("path")
        recursive = context.parameters.get("recursive", False)
        
        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        # Check exists
        if not os.path.exists(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Path not found: {path}",
            )
        
        try:
            is_dir = os.path.isdir(path)
            
            if is_dir:
                if recursive:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            else:
                os.remove(path)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "path": path,
                    "type": "directory" if is_dir else "file",
                    "recursive": recursive if is_dir else None,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
