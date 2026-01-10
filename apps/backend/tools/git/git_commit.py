"""Git commit tool.

Creates git commits.

Capabilities:
- Create commits
- Stage and commit
- Amend commits
- Multi-line messages
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


class GitCommitTool(BaseTool):
    """Create git commits.

    Example:
        tool = GitCommitTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "message": "feat: add new feature",
            }
        ))
    """

    name = "git_commit"
    description = "Create git commits"
    category = ToolCategory.GIT
    required_permissions = {"git_write"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="message",
                type="string",
                description="Commit message",
                required=True,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Repository path",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="files",
                type="array",
                description="Files to stage before commit",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="all",
                type="boolean",
                description="Stage all changes",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="amend",
                type="boolean",
                description="Amend previous commit",
                required=False,
                default=False,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git commit."""
        message = context.parameters.get("message")
        path = context.parameters.get("path", context.working_directory)
        files = context.parameters.get("files")
        stage_all = context.parameters.get("all", False)
        amend = context.parameters.get("amend", False)

        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        try:
            # Stage files if specified
            if files:
                for f in files:
                    subprocess.run(
                        ["git", "add", f],
                        cwd=path,
                        capture_output=True,
                        timeout=10,
                    )
            elif stage_all:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=path,
                    capture_output=True,
                    timeout=10,
                )

            # Create commit
            cmd = ["git", "commit", "-m", message]
            if amend:
                cmd.append("--amend")

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
                    error=result.stderr or result.stdout,
                )

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=path,
                capture_output=True,
                text=True,
            )

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "message": message,
                    "commit_hash": hash_result.stdout.strip(),
                    "amend": amend,
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
