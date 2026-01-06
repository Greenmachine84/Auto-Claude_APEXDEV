"""Git diff tool.

Shows git diffs.

Capabilities:
- Staged vs unstaged
- Between commits
- Specific files
- Stat summaries
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


class GitDiffTool(BaseTool):
    """Show git diffs.
    
    Example:
        tool = GitDiffTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={"staged": True}
        ))
    """
    
    name = "git_diff"
    description = "Show git diffs"
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
                name="staged",
                type="boolean",
                description="Show staged changes",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="commit",
                type="string",
                description="Compare with specific commit",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="file",
                type="string",
                description="Specific file to diff",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="stat",
                type="boolean",
                description="Show stat summary only",
                required=False,
                default=False,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git diff."""
        path = context.parameters.get("path", context.working_directory)
        staged = context.parameters.get("staged", False)
        commit = context.parameters.get("commit")
        file = context.parameters.get("file")
        stat = context.parameters.get("stat", False)
        
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            cmd = ["git", "diff"]
            
            if staged:
                cmd.append("--cached")
            if commit:
                cmd.append(commit)
            if stat:
                cmd.append("--stat")
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
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "diff": result.stdout,
                    "staged": staged,
                    "commit": commit,
                    "file": file,
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
