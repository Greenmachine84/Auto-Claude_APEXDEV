"""Git branch tool.

Manages git branches.

Capabilities:
- List branches
- Create branches
- Switch branches
- Delete branches
"""

import os
import subprocess

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)


class GitBranchTool(BaseTool):
    """Manage git branches.

    Example:
        tool = GitBranchTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "action": "create",
                "name": "feature/new-feature",
            }
        ))
    """

    name = "git_branch"
    description = "Manage git branches"
    category = ToolCategory.GIT
    required_permissions = {"git_read", "git_write"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action: list, create, switch, delete",
                required=True,
                enum=["list", "create", "switch", "delete"],
            ),
            ToolParameter(
                name="name",
                type="string",
                description="Branch name (for create/switch/delete)",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Repository path",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="force",
                type="boolean",
                description="Force the operation",
                required=False,
                default=False,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git branch operation."""
        action = context.parameters.get("action")
        name = context.parameters.get("name")
        path = context.parameters.get("path", context.working_directory)
        force = context.parameters.get("force", False)

        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        try:
            if action == "list":
                return await self._list_branches(path)
            elif action == "create":
                if not name:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error="Branch name required for create",
                    )
                return await self._create_branch(path, name)
            elif action == "switch":
                if not name:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error="Branch name required for switch",
                    )
                return await self._switch_branch(path, name, force)
            elif action == "delete":
                if not name:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error="Branch name required for delete",
                    )
                return await self._delete_branch(path, name, force)

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )

    async def _list_branches(self, path: str) -> ToolResult:
        """List all branches."""
        result = subprocess.run(
            ["git", "branch", "-a", "--format=%(refname:short)"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        branches = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Get current branch
        current = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=path,
            capture_output=True,
            text=True,
        )

        return ToolResult(
            tool_name=self.name,
            status=ToolStatus.COMPLETED,
            output={
                "branches": branches,
                "current": current.stdout.strip(),
                "count": len(branches),
            },
        )

    async def _create_branch(self, path: str, name: str) -> ToolResult:
        """Create new branch."""
        result = subprocess.run(
            ["git", "branch", name],
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
            output={"branch": name, "action": "created"},
        )

    async def _switch_branch(self, path: str, name: str, force: bool) -> ToolResult:
        """Switch to branch."""
        cmd = ["git", "checkout", name]
        if force:
            cmd.insert(2, "-f")

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
            output={"branch": name, "action": "switched"},
        )

    async def _delete_branch(self, path: str, name: str, force: bool) -> ToolResult:
        """Delete branch."""
        cmd = ["git", "branch", "-D" if force else "-d", name]

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
            output={"branch": name, "action": "deleted"},
        )
