"""Grep search tool.

Fast text search using grep-like functionality.

Capabilities:
- Pattern matching
- Regex support
- Case sensitivity
- Context lines
"""

from typing import Any, Dict, List, Optional
import subprocess
import os

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class GrepSearchTool(BaseTool):
    """Fast text search.
    
    Example:
        tool = GrepSearchTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/search",
                "pattern": "TODO:",
            }
        ))
    """
    
    name = "grep_search"
    description = "Fast text search using grep"
    category = ToolCategory.SEARCH
    required_permissions = {"read_files"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="pattern",
                type="string",
                description="Pattern to search for",
                required=True,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Directory or file to search",
                required=True,
            ),
            ToolParameter(
                name="regex",
                type="boolean",
                description="Use regex patterns",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="case_sensitive",
                type="boolean",
                description="Case sensitive search",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="context",
                type="integer",
                description="Lines of context around match",
                required=False,
                default=0,
            ),
            ToolParameter(
                name="include",
                type="string",
                description="File pattern to include",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum results",
                required=False,
                default=100,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute grep search."""
        pattern = context.parameters.get("pattern")
        path = context.parameters.get("path")
        use_regex = context.parameters.get("regex", False)
        case_sensitive = context.parameters.get("case_sensitive", True)
        ctx_lines = context.parameters.get("context", 0)
        include = context.parameters.get("include")
        max_results = context.parameters.get("max_results", 100)
        
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            # Build grep command
            cmd = ["grep", "-rn"]
            
            if use_regex:
                cmd.append("-E")
            else:
                cmd.append("-F")
            
            if not case_sensitive:
                cmd.append("-i")
            
            if ctx_lines > 0:
                cmd.extend(["-C", str(ctx_lines)])
            
            if include:
                cmd.extend(["--include", include])
            
            cmd.extend([pattern, path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            # Parse results
            matches = []
            for line in result.stdout.split("\n"):
                if not line or len(matches) >= max_results:
                    continue
                
                # Parse grep output: file:line:content
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    matches.append({
                        "file": os.path.relpath(parts[0], path),
                        "line": int(parts[1]) if parts[1].isdigit() else 0,
                        "text": parts[2][:200],
                    })
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "matches": matches,
                    "count": len(matches),
                    "pattern": pattern,
                },
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.TIMEOUT,
                output=None,
                error="Search timed out",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
