"""File search tool.

Searches for files.

Capabilities:
- Search by name pattern
- Search by content
- Recursive search
- Filter by type/size/date
"""

from typing import Any, Dict, List, Optional
import os
import fnmatch
import re

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class FileSearchTool(BaseTool):
    """Search for files.
    
    Searches for files by name pattern or content.
    
    Example:
        tool = FileSearchTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "path": "/path/to/search",
                "pattern": "*.py",
            }
        ))
    """
    
    name = "file_search"
    description = "Search for files"
    category = ToolCategory.FILESYSTEM
    required_permissions = {"read_files"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Directory to search in",
                required=True,
            ),
            ToolParameter(
                name="pattern",
                type="string",
                description="Glob pattern to match file names",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Content to search for in files",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="regex",
                type="boolean",
                description="Treat content as regex",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of results",
                required=False,
                default=100,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute file search.
        
        Args:
            context: Execution context with search params
            
        Returns:
            ToolResult with search results
        """
        path = context.parameters.get("path")
        pattern = context.parameters.get("pattern")
        content = context.parameters.get("content")
        use_regex = context.parameters.get("regex", False)
        max_results = context.parameters.get("max_results", 100)
        
        # Resolve path
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        if not os.path.exists(path):
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Path not found: {path}",
            )
        
        try:
            results = []
            
            for root, dirs, files in os.walk(path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                
                for name in files:
                    if len(results) >= max_results:
                        break
                    
                    # Check pattern
                    if pattern and not fnmatch.fnmatch(name, pattern):
                        continue
                    
                    full_path = os.path.join(root, name)
                    rel_path = os.path.relpath(full_path, path)
                    
                    # Check content if specified
                    if content:
                        matches = self._search_content(
                            full_path, content, use_regex
                        )
                        if matches:
                            results.append({
                                "path": rel_path,
                                "matches": matches,
                            })
                    else:
                        results.append({"path": rel_path})
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "search_path": path,
                    "results": results,
                    "count": len(results),
                    "truncated": len(results) >= max_results,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
    
    def _search_content(
        self,
        path: str,
        search: str,
        use_regex: bool,
    ) -> List[Dict[str, Any]]:
        """Search file content."""
        matches = []
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if use_regex:
                        if re.search(search, line):
                            matches.append({
                                "line": i,
                                "text": line.strip()[:200],
                            })
                    else:
                        if search in line:
                            matches.append({
                                "line": i,
                                "text": line.strip()[:200],
                            })
        except Exception:
            pass
        
        return matches[:10]  # Limit matches per file
