"""
Git Tools - Phase 8 Builtin.

Consolidated git operations.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging

from ..models import Tool, ToolCategory, ToolParameter, ParameterType, ToolResult, ToolExecutionContext

logger = logging.getLogger(__name__)


class GitTools:
    """Git operation tools."""
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get all git tools."""
        return [
            GitTools._git_status_tool(),
            GitTools._git_diff_tool(),
            GitTools._git_log_tool(),
            GitTools._git_commit_tool(),
        ]
    
    @staticmethod
    def _git_status_tool() -> Tool:
        return Tool(
            name="git_status",
            description="Get git repository status",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(name="path", type=ParameterType.FILE_PATH, description="Repository path", default="."),
            ],
            handler=GitTools.git_status,
            tags=["git", "status"],
        )
    
    @staticmethod
    def _git_diff_tool() -> Tool:
        return Tool(
            name="git_diff",
            description="Show git diff",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(name="path", type=ParameterType.FILE_PATH, description="Repository path", default="."),
                ToolParameter(name="staged", type=ParameterType.BOOLEAN, description="Show staged changes", default=False),
            ],
            handler=GitTools.git_diff,
            tags=["git", "diff"],
        )
    
    @staticmethod
    def _git_log_tool() -> Tool:
        return Tool(
            name="git_log",
            description="Show git log",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(name="path", type=ParameterType.FILE_PATH, description="Repository path", default="."),
                ToolParameter(name="limit", type=ParameterType.INTEGER, description="Number of commits", default=10),
            ],
            handler=GitTools.git_log,
            tags=["git", "log"],
        )
    
    @staticmethod
    def _git_commit_tool() -> Tool:
        return Tool(
            name="git_commit",
            description="Create git commit",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(name="message", type=ParameterType.STRING, description="Commit message", required=True),
                ToolParameter(name="path", type=ParameterType.FILE_PATH, description="Repository path", default="."),
            ],
            handler=GitTools.git_commit,
            requires_confirmation=True,
            tags=["git", "commit"],
        )
    
    @staticmethod
    async def _run_git(cmd: str, cwd: str = ".") -> tuple:
        """Run git command."""
        proc = await asyncio.create_subprocess_shell(
            cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode(), stderr.decode()
    
    @staticmethod
    async def git_status(ctx: ToolExecutionContext, path: str = ".") -> ToolResult:
        """Get git status."""
        code, out, err = await GitTools._run_git("git status --porcelain", path)
        if code != 0:
            return ToolResult(output=None, error=err, metadata={"path": path})
        return ToolResult(output=out, error=None, metadata={"path": path})
    
    @staticmethod
    async def git_diff(ctx: ToolExecutionContext, path: str = ".", staged: bool = False) -> ToolResult:
        """Get git diff."""
        cmd = "git diff --cached" if staged else "git diff"
        code, out, err = await GitTools._run_git(cmd, path)
        if code != 0:
            return ToolResult(output=None, error=err, metadata={"path": path})
        return ToolResult(output=out, error=None, metadata={"path": path})
    
    @staticmethod
    async def git_log(ctx: ToolExecutionContext, path: str = ".", limit: int = 10) -> ToolResult:
        """Get git log."""
        code, out, err = await GitTools._run_git(f"git log --oneline -n {limit}", path)
        if code != 0:
            return ToolResult(output=None, error=err, metadata={"path": path})
        return ToolResult(output=out, error=None, metadata={"path": path})
    
    @staticmethod
    async def git_commit(ctx: ToolExecutionContext, message: str, path: str = ".") -> ToolResult:
        """Create git commit."""
        code, out, err = await GitTools._run_git(f'git commit -m "{message}"', path)
        if code != 0:
            return ToolResult(output=None, error=err, metadata={"path": path})
        return ToolResult(output=out, error=None, metadata={"path": path})
