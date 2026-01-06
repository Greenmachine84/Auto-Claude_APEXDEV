"""Directory create tool.

Creates directories.

Capabilities:
- Create single directories
- Create nested directories
- Set permissions
"""

from typing import Any, Dict, List, Optional
import os

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class DirectoryCreateTool(BaseTool):
    """Create directories.
    
    Creates new directories with optional nested creation.
    
    Example:
        tool = DirectoryCreateTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/new/dir",
            }
        ))
    """
    
    name = "directory_create"
    description = "Create directories"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"create_dirs"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Directory path to create",
                required=True,
            ),
            ToolParameter(
                name="parents",
                type="boolean",
                description="Create parent directories as needed",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="exist_ok",
                type="boolean",
                description="Don't error if directory exists",
                required=False,
                default=True,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute directory creation.
        
        Args:
            context: Execution context with path
            
        Returns:
            ToolResult with creation status
        """
        path = context.parameters.get("path")
        parents = context.parameters.get("parents", True)
        exist_ok = context.parameters.get("exist_ok", True)
        
        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            existed = os.path.exists(path)
            
            if parents:
                os.makedirs(path, exist_ok=exist_ok)
            else:
                if exist_ok and os.path.exists(path):
                    pass
                else:
                    os.mkdir(path)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "path": path,
                    "created": not existed,
                    "existed": existed,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
