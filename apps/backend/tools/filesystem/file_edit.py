"""File edit tool.

Edits file content in place.

Capabilities:
- Replace text in files
- Insert at specific lines
- Delete line ranges
- Search and replace
"""

from typing import Any, Dict, List, Optional
import os
import re

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class FileEditTool(BaseTool):
    """Edit file content in place.
    
    Performs precise edits on file content including
    replacements, insertions, and deletions.
    
    Example:
        tool = FileEditTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/file.txt",
                "old_text": "old value",
                "new_text": "new value",
            }
        ))
    """
    
    name = "file_edit"
    description = "Edit file content in place"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"read_files", "write_files"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Path to file to edit",
                required=True,
            ),
            ToolParameter(
                name="old_text",
                type="string",
                description="Text to replace",
                required=True,
            ),
            ToolParameter(
                name="new_text",
                type="string",
                description="Replacement text",
                required=True,
            ),
            ToolParameter(
                name="occurrence",
                type="string",
                description="Which occurrence: 'first', 'last', or 'all'",
                required=False,
                default="first",
                enum=["first", "last", "all"],
            ),
            ToolParameter(
                name="regex",
                type="boolean",
                description="Treat old_text as regex pattern",
                required=False,
                default=False,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute file edit.
        
        Args:
            context: Execution context with edit parameters
            
        Returns:
            ToolResult with edit status
        """
        path = context.parameters.get("path")
        old_text = context.parameters.get("old_text")
        new_text = context.parameters.get("new_text")
        occurrence = context.parameters.get("occurrence", "first")
        use_regex = context.parameters.get("regex", False)
        
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
        
        try:
            # Read current content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Perform replacement
            if use_regex:
                content, count = self._regex_replace(
                    content, old_text, new_text, occurrence
                )
            else:
                content, count = self._text_replace(
                    content, old_text, new_text, occurrence
                )
            
            if count == 0:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    output=None,
                    error="Text not found in file",
                )
            
            # Write updated content
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "path": path,
                    "replacements": count,
                    "occurrence": occurrence,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
    
    def _text_replace(
        self,
        content: str,
        old_text: str,
        new_text: str,
        occurrence: str,
    ) -> tuple:
        """Replace text in content."""
        if occurrence == "all":
            count = content.count(old_text)
            return content.replace(old_text, new_text), count
        elif occurrence == "first":
            if old_text in content:
                return content.replace(old_text, new_text, 1), 1
            return content, 0
        elif occurrence == "last":
            idx = content.rfind(old_text)
            if idx >= 0:
                return content[:idx] + new_text + content[idx + len(old_text):], 1
            return content, 0
        return content, 0
    
    def _regex_replace(
        self,
        content: str,
        pattern: str,
        replacement: str,
        occurrence: str,
    ) -> tuple:
        """Replace using regex."""
        if occurrence == "all":
            new_content, count = re.subn(pattern, replacement, content)
            return new_content, count
        elif occurrence == "first":
            new_content, count = re.subn(pattern, replacement, content, count=1)
            return new_content, count
        elif occurrence == "last":
            matches = list(re.finditer(pattern, content))
            if matches:
                last = matches[-1]
                return content[:last.start()] + replacement + content[last.end():], 1
            return content, 0
        return content, 0
