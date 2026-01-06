"""Process spawn tool.

Spawns background processes.

Capabilities:
- Start background processes
- Track process IDs
- Manage process lifecycle
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


# Track spawned processes
_spawned_processes: Dict[int, subprocess.Popen] = {}


class ProcessSpawnTool(BaseTool):
    """Spawn background processes.
    
    Example:
        tool = ProcessSpawnTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "command": "python server.py",
            }
        ))
    """
    
    name = "process_spawn"
    description = "Spawn background processes"
    category = ToolCategory.TERMINAL
    required_permissions = {"spawn_processes"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="command",
                type="string",
                description="Command to spawn",
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
        """Spawn process."""
        command = context.parameters.get("command")
        cwd = context.parameters.get("cwd", context.working_directory)
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
            
            # Spawn process
            if shell:
                args = command
            else:
                args = shlex.split(command)
            
            process = subprocess.Popen(
                args,
                shell=shell,
                cwd=cwd,
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Track process
            _spawned_processes[process.pid] = process
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "pid": process.pid,
                    "command": command,
                    "status": "running",
                },
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
