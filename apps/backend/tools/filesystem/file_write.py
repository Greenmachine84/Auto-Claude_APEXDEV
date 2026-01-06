"""File write tool.

Writes content to files.

Capabilities:
- Create new files
- Overwrite existing files
- Append to files
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


class FileWriteTool(BaseTool):
    """Write content to files.
    
    Creates or overwrites files with specified content.
    
    Example:
        tool = FileWriteTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/file.txt",
                "content": "Hello, World!",
            }
        ))
    """
    
    name = "file_write"
    description = "Write content to a file"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"write_files"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Path to file to write",
                required=True,
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Content to write",
                required=True,
            ),
            ToolParameter(
                name="mode",
                type="string",
                description="Write mode: 'overwrite' or 'append'",
                required=False,
                default="overwrite",
                enum=["overwrite", "append"],
            ),
            ToolParameter(
                name="create_dirs",
                type="boolean",
                description="Create parent directories if needed",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding",
                required=False,
                default="utf-8",
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute file write.
        
        Args:
            context: Execution context with path and content
            
        Returns:
            ToolResult with write status
        """
        path = context.parameters.get("path")
        content = context.parameters.get("content")
        mode = context.parameters.get("mode", "overwrite")
        create_dirs = context.parameters.get("create_dirs", True)
        encoding = context.parameters.get("encoding", "utf-8")
        
        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            # Create parent directories if needed
            if create_dirs:
                parent = os.path.dirname(path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent)
            
            # Determine file mode
            file_mode = "a" if mode == "append" else "w"
            
            # Get file size before (if exists)
            existed = os.path.exists(path)
            size_before = os.path.getsize(path) if existed else 0
            
            # Write file
            with open(path, file_mode, encoding=encoding) as f:
                f.write(content)
            
            # Get file size after
            size_after = os.path.getsize(path)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "path": path,
                    "bytes_written": len(content.encode(encoding)),
                    "file_size": size_after,
                    "created": not existed,
                    "mode": mode,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
