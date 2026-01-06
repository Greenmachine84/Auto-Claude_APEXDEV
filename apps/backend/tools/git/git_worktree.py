"""Git worktree tool.

Manages git worktrees.

Capabilities:
- List worktrees
- Add worktrees
- Remove worktrees
- Prune worktrees
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


class GitWorktreeTool(BaseTool):
    """Manage git worktrees.
    
    Example:
        tool = GitWorktreeTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "action": "add",
                "worktree_path": "../feature-branch",
                "branch": "feature/new",
            }
        ))
    """
    
    name = "git_worktree"
    description = "Manage git worktrees"
    category = ToolCategory.GIT
    required_permissions = {"git_read", "git_write"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action: list, add, remove, prune",
                required=True,
                enum=["list", "add", "remove", "prune"],
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Repository path",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="worktree_path",
                type="string",
                description="Path for new worktree",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="branch",
                type="string",
                description="Branch for worktree",
                required=False,
                default=None,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git worktree operation."""
        action = context.parameters.get("action")
        path = context.parameters.get("path", context.working_directory)
        worktree_path = context.parameters.get("worktree_path")
        branch = context.parameters.get("branch")
        
        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)
        
        try:
            if action == "list":
                return await self._list_worktrees(path)
            elif action == "add":
                if not worktree_path:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error="Worktree path required for add",
                    )
                return await self._add_worktree(path, worktree_path, branch)
            elif action == "remove":
                if not worktree_path:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error="Worktree path required for remove",
                    )
                return await self._remove_worktree(path, worktree_path)
            elif action == "prune":
                return await self._prune_worktrees(path)
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
    
    async def _list_worktrees(self, path: str) -> ToolResult:
        """List worktrees."""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        worktrees = []
        current = {}
        
        for line in result.stdout.split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line[9:]}
            elif line.startswith("HEAD "):
                current["head"] = line[5:]
            elif line.startswith("branch "):
                current["branch"] = line[7:]
        
        if current:
            worktrees.append(current)
        
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            output={
                "worktrees": worktrees,
                "count": len(worktrees),
            },
        )
    
    async def _add_worktree(self, path: str, worktree_path: str, branch: Optional[str]) -> ToolResult:
        """Add worktree."""
        cmd = ["git", "worktree", "add", worktree_path]
        if branch:
            cmd.append(branch)
        
        result = subprocess.run(
            cmd,
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
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
                "worktree": worktree_path,
                "branch": branch,
                "action": "added",
            },
        )
    
    async def _remove_worktree(self, path: str, worktree_path: str) -> ToolResult:
        """Remove worktree."""
        result = subprocess.run(
            ["git", "worktree", "remove", worktree_path],
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
            output={"worktree": worktree_path, "action": "removed"},
        )
    
    async def _prune_worktrees(self, path: str) -> ToolResult:
        """Prune stale worktrees."""
        result = subprocess.run(
            ["git", "worktree", "prune"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            output={"action": "pruned"},
        )
