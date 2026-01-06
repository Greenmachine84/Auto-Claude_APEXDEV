"""Command execute tool.

Executes shell commands.

Capabilities:
- Run shell commands
- Capture output
- Set working directory
- Handle timeouts
"""

from typing import Any, Dict, List, Optional
import subprocess
import os
import shlex

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class CommandExecuteTool(BaseTool):
    """Execute shell commands.
    
    Example:
        tool = CommandExecuteTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "command": "ls -la",
            }
        ))
    """
    
    name = "command_execute"
    description = "Execute shell commands"
    category = ToolCategory.TERMINAL
    required_permissions = {"execute_commands"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="command",
                type="string",
                description="Command to execute",
                required=True,
            ),
            ToolParameter(
                name="cwd",
                type="string",
                description="Working directory",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Timeout in seconds",
                required=False,
                default=60,
            ),
            ToolParameter(
                name="shell",
                type="boolean",
                description="Execute through shell",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="env",
                type="object",
                description="Environment variables",
                required=False,
                default=None,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute command."""
        command = context.parameters.get("command")
        cwd = context.parameters.get("cwd", context.working_directory)
        timeout = context.parameters.get("timeout", 60)
        shell = context.parameters.get("shell", True)
        env = context.parameters.get("env")
        
        if cwd and not os.path.isabs(cwd):
            cwd = os.path.join(context.working_directory, cwd)
        
        try:
            # Merge environment
            process_env = os.environ.copy()
            process_env.update(context.environment)
            if env:
                process_env.update(env)
            
            # Execute command
            if shell:
                args = command
            else:
                args = shlex.split(command)
            
            result = subprocess.run(
                args,
                shell=shell,
                cwd=cwd,
                env=process_env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode,
                    "command": command,
                },
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.TIMEOUT,
                output=None,
                error=f"Command timed out after {timeout}s",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
