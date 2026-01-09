"""Process kill tool.

Terminates processes.

Capabilities:
- Kill by PID
- Signal processes
- Force termination
"""

import os
import signal

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolParameter,
    ToolResult,
    ToolStatus,
)

# Import tracked processes
from tools.terminal.process_spawn import _spawned_processes


class ProcessKillTool(BaseTool):
    """Terminate processes.

    Example:
        tool = ProcessKillTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "pid": 12345,
            }
        ))
    """

    name = "process_kill"
    description = "Terminate processes"
    category = ToolCategory.TERMINAL
    required_permissions = {"spawn_processes"}
    version = "1.0.0"

    def get_parameters(self) -> list[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="pid",
                type="integer",
                description="Process ID to kill",
                required=True,
            ),
            ToolParameter(
                name="signal",
                type="string",
                description="Signal to send: SIGTERM, SIGKILL, etc.",
                required=False,
                default="SIGTERM",
            ),
            ToolParameter(
                name="force",
                type="boolean",
                description="Use SIGKILL",
                required=False,
                default=False,
            ),
        ]

    async def execute(self, context: ToolContext) -> ToolResult:
        """Kill process."""
        pid = context.parameters.get("pid")
        sig = context.parameters.get("signal", "SIGTERM")
        force = context.parameters.get("force", False)

        try:
            # Determine signal
            if force:
                sig_num = signal.SIGKILL
            else:
                sig_num = getattr(signal, sig, signal.SIGTERM)

            # Check if we're tracking this process
            if pid in _spawned_processes:
                process = _spawned_processes[pid]
                if force:
                    process.kill()
                else:
                    process.terminate()
                del _spawned_processes[pid]
            else:
                # Kill external process
                os.kill(pid, sig_num)

            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output={
                    "pid": pid,
                    "signal": sig,
                    "terminated": True,
                },
            )

        except ProcessLookupError:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Process {pid} not found",
            )
        except PermissionError:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Permission denied to kill process {pid}",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
