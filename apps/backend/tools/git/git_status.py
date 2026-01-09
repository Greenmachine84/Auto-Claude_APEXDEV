"""Git status tool.

Shows git repository status.

Capabilities:
- Show modified files
- Show staged files
- Show untracked files
- Branch information
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


class GitStatusTool(BaseTool):
    """Show git repository status.

    Example:
        tool = GitStatusTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={"path": "/path/to/repo"}
        ))
    """

    name = "git_status"
    description = "Show git repository status"
    category = ToolCategory.GIT
    required_permissions = {"git_read"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="path",
                type="string",
                description="Repository path",
                required=False,
                default=".",
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute git status."""
        path = context.parameters.get("path", context.working_directory)

        if not os.path.isabs(path):
            path = os.path.join(context.working_directory, path)

        try:
            # Get porcelain status
            result = subprocess.run(
                ["git", "status", "--porcelain=v1", "-b"],
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

            # Parse status
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            branch = None
            staged = []
            modified = []
            untracked = []

            for line in lines:
                if line.startswith("## "):
                    branch = line[3:].split("...")[0]
                    continue

                if not line or len(line) < 3:
                    continue

                status_code = line[:2]
                filename = line[3:]

                if status_code[0] != " " and status_code[0] != "?":
                    staged.append({"status": status_code[0], "file": filename})
                if status_code[1] != " " and status_code[1] != "?":
                    modified.append({"status": status_code[1], "file": filename})
                if status_code == "??":
                    untracked.append(filename)

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "branch": branch,
                    "staged": staged,
                    "modified": modified,
                    "untracked": untracked,
                    "clean": len(staged) == 0
                    and len(modified) == 0
                    and len(untracked) == 0,
                },
            )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
