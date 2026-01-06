"""Git log tool.

Shows git commit history.

Capabilities:
- View commit log
- Filter by author
- Filter by date
- Limit results
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


class GitLogTool(BaseTool):
    """Show git commit history.
    
    Example:
        tool = GitLogTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={"limit": 10}
        ))
    """
    
    name = "git_log"
    description = "Show git commit history"
    category = ToolCategory.GIT
    required_permissions = {"git_read"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Repository path",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Maximum commits to show",
                required=False,
                default=20,
            ),
            ToolParameter(
                name="author",
                type="string",
                description="Filter by author",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="since",
                type="string",
                description="Show commits since date",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="file",
                type="string",
                description="Show commits for specific file",
                required=False,
                default=None,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git log."""
        path = context.parameters.get("path", context.working_directory)
        limit = context.parameters.get("limit", 20)
        author = context.parameters.get("author")
        since = context.parameters.get("since")
        file = context.parameters.get("file")
        
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            # Build command
            cmd = [
                "git", "log",
                f"--max-count={limit}",
                "--format=%H|%an|%ae|%at|%s",
            ]
            
            if author:
                cmd.append(f"--author={author}")
            if since:
                cmd.append(f"--since={since}")
            if file:
                cmd.extend(["--", file])
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode != 0:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    output=None,
                    error=result.stderr,
                )
            
            # Parse commits
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "timestamp": int(parts[3]),
                        "message": parts[4],
                    })
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "commits": commits,
                    "count": len(commits),
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
