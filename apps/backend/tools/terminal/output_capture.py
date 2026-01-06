"""Output capture tool.

Captures process output.

Capabilities:
- Get stdout/stderr
- Stream output
- Check process status
"""

from typing import Any, Dict, List, Optional

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


# Import tracked processes
from tools.terminal.process_spawn import _spawned_processes


class OutputCaptureTool(BaseTool):
    """Capture process output.
    
    Example:
        tool = OutputCaptureTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "pid": 12345,
            }
        ))
    """
    
    name = "output_capture"
    description = "Capture process output"
    category = ToolCategory.TERMINAL
    required_permissions = {"execute_commands"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="pid",
                type="integer",
                description="Process ID to capture from",
                required=True,
            ),
            ToolParameter(
                name="wait",
                type="boolean",
                description="Wait for process to complete",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Timeout for wait in seconds",
                required=False,
                default=30,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Capture output."""
        pid = context.parameters.get("pid")
        wait = context.parameters.get("wait", False)
        timeout = context.parameters.get("timeout", 30)
        
        try:
            if pid not in _spawned_processes:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    output=None,
                    error=f"Process {pid} not tracked",
                )
            
            process = _spawned_processes[pid]
            
            if wait:
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    stdout = stdout.decode() if stdout else ""
                    stderr = stderr.decode() if stderr else ""
                    
                    # Process completed, remove from tracking
                    del _spawned_processes[pid]
                    
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.COMPLETED,
                        output={
                            "pid": pid,
                            "stdout": stdout,
                            "stderr": stderr,
                            "exit_code": process.returncode,
                            "status": "completed",
                        },
                    )
                except Exception:
                    return ToolResult(
                        tool_name=self.name,
                        status=ToolStatus.TIMEOUT,
                        output=None,
                        error=f"Process did not complete within {timeout}s",
                    )
            else:
                # Just check status
                poll = process.poll()
                
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.COMPLETED,
                    output={
                        "pid": pid,
                        "status": "completed" if poll is not None else "running",
                        "exit_code": poll,
                    },
                )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
