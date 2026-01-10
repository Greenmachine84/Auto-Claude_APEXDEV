"""
Shell Tools - Phase 8 Builtin.

Consolidated shell operations.
"""

import asyncio
import logging

from ..models import (
    ParameterType,
    Tool,
    ToolCategory,
    ToolExecutionContext,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class ShellTools:
    """Shell operation tools."""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Get all shell tools."""
        return [
            ShellTools._run_command_tool(),
            ShellTools._run_script_tool(),
        ]

    @staticmethod
    def _run_command_tool() -> Tool:
        return Tool(
            name="run_command",
            description="Run shell command",
            category=ToolCategory.SHELL,
            parameters=[
                ToolParameter(
                    name="command",
                    type=ParameterType.STRING,
                    description="Command to run",
                    required=True,
                ),
                ToolParameter(
                    name="cwd",
                    type=ParameterType.FILE_PATH,
                    description="Working directory",
                    default=".",
                ),
                ToolParameter(
                    name="timeout",
                    type=ParameterType.INTEGER,
                    description="Timeout in seconds",
                    default=60,
                ),
            ],
            handler=ShellTools.run_command,
            requires_confirmation=True,
            permissions=["shell_execute"],
            tags=["shell", "command"],
        )

    @staticmethod
    def _run_script_tool() -> Tool:
        return Tool(
            name="run_script",
            description="Run shell script",
            category=ToolCategory.SHELL,
            parameters=[
                ToolParameter(
                    name="script",
                    type=ParameterType.STRING,
                    description="Script content",
                    required=True,
                ),
                ToolParameter(
                    name="shell",
                    type=ParameterType.STRING,
                    description="Shell to use",
                    default="bash",
                ),
                ToolParameter(
                    name="cwd",
                    type=ParameterType.FILE_PATH,
                    description="Working directory",
                    default=".",
                ),
            ],
            handler=ShellTools.run_script,
            requires_confirmation=True,
            permissions=["shell_execute"],
            tags=["shell", "script"],
        )

    @staticmethod
    async def run_command(
        ctx: ToolExecutionContext, command: str, cwd: str = ".", timeout: int = 60
    ) -> ToolResult:
        """Run shell command."""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            return ToolResult(
                output={
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": proc.returncode,
                },
                error=None if proc.returncode == 0 else f"Exit code: {proc.returncode}",
                metadata={"command": command, "cwd": cwd},
            )
        except asyncio.TimeoutError:
            return ToolResult(
                output=None,
                error=f"Timeout after {timeout}s",
                metadata={"command": command},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"command": command})

    @staticmethod
    async def run_script(
        ctx: ToolExecutionContext, script: str, shell: str = "bash", cwd: str = "."
    ) -> ToolResult:
        """Run shell script."""
        try:
            proc = await asyncio.create_subprocess_exec(
                shell,
                "-c",
                script,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            return ToolResult(
                output={
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": proc.returncode,
                },
                error=None if proc.returncode == 0 else f"Exit code: {proc.returncode}",
                metadata={"shell": shell, "cwd": cwd},
            )
        except Exception as e:
            return ToolResult(output=None, error=str(e), metadata={"shell": shell})
