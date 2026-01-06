"""Step executor.

Executes workflow steps.

Capabilities:
- Step type routing
- Input/output handling
- Error handling
- Timeout management
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

from orchestrator.workflow.definition import WorkflowStep


logger = logging.getLogger(__name__)


# Type alias for step handlers
StepHandler = Callable[[WorkflowStep, Dict[str, Any]], Any]


class StepExecutor:
    """Execute workflow steps.
    
    Routes steps to appropriate handlers.
    
    Example:
        executor = StepExecutor()
        executor.register_handler("build", build_handler)
        result = await executor.execute(step, inputs)
    """
    
    def __init__(self):
        """Initialize executor."""
        self._handlers: Dict[str, StepHandler] = {}
        self._default_handler: Optional[StepHandler] = None
        
        logger.debug("StepExecutor initialized")
    
    def register_handler(
        self,
        step_type: str,
        handler: StepHandler,
    ) -> None:
        """Register a step handler."""
        self._handlers[step_type] = handler
        logger.debug(f"Registered handler for step type: {step_type}")
    
    def set_default_handler(self, handler: StepHandler) -> None:
        """Set default handler for unknown types."""
        self._default_handler = handler
    
    async def execute(
        self,
        step: WorkflowStep,
        inputs: Dict[str, Any],
    ) -> Any:
        """Execute a step."""
        handler = self._handlers.get(step.type) or self._default_handler
        
        if not handler:
            raise ValueError(f"No handler for step type: {step.type}")
        
        logger.debug(f"Executing step {step.id} of type {step.type}")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_handler(handler, step, inputs),
                timeout=step.timeout,
            )
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Step {step.id} timed out after {step.timeout}s")
    
    async def _run_handler(
        self,
        handler: StepHandler,
        step: WorkflowStep,
        inputs: Dict[str, Any],
    ) -> Any:
        """Run handler (sync or async)."""
        result = handler(step, inputs)
        
        if asyncio.iscoroutine(result):
            return await result
        
        return result
    
    def list_handlers(self) -> list[str]:
        """List registered handler types."""
        return list(self._handlers.keys())


# Built-in handlers
async def noop_handler(step: WorkflowStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """No-op handler for testing."""
    return {"step_id": step.id, "status": "completed"}


async def shell_handler(step: WorkflowStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute shell command."""
    import subprocess
    
    command = inputs.get("command") or step.inputs.get("command")
    if not command:
        raise ValueError("No command specified")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=step.timeout,
    )
    
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


async def python_handler(step: WorkflowStep, inputs: Dict[str, Any]) -> Any:
    """Execute Python code."""
    code = inputs.get("code") or step.inputs.get("code")
    if not code:
        raise ValueError("No code specified")
    
    # Create execution context
    context = {"inputs": inputs, "result": None}
    
    exec(code, context)
    
    return context.get("result")
