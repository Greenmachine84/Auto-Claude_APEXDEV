"""Workflow engine.

Executes workflow definitions.

Capabilities:
- Step execution
- Parallel steps
- Conditional branching
- Error handling
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from orchestrator.workflow.definition import WorkflowDefinition, WorkflowStep
from orchestrator.workflow.state import StepState, WorkflowState, WorkflowStatus
from orchestrator.workflow.step_executor import StepExecutor

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Execute workflows.

    Runs workflow definitions with step coordination.

    Example:
        engine = WorkflowEngine()
        workflow = WorkflowDefinition(...)
        result = await engine.run(workflow)
    """

    def __init__(self, max_concurrent: int = 4):
        """Initialize engine."""
        self.max_concurrent = max_concurrent
        self._running: dict[str, WorkflowState] = {}
        self._executor = StepExecutor()
        self._lock = asyncio.Lock()

        logger.debug("WorkflowEngine initialized")

    async def run(
        self,
        workflow: WorkflowDefinition,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowState:
        """Run a workflow."""
        # Create state
        state = WorkflowState(
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            inputs=inputs or {},
        )

        async with self._lock:
            self._running[state.workflow_id] = state

        try:
            state.status = WorkflowStatus.RUNNING
            state.started_at = datetime.now()

            logger.info(f"Starting workflow {workflow.id}")

            # Execute steps
            await self._execute_workflow(workflow, state)

            # Set final status
            if state.has_failures:
                state.status = WorkflowStatus.FAILED
            else:
                state.status = WorkflowStatus.COMPLETED

        except asyncio.CancelledError:
            state.status = WorkflowStatus.CANCELLED
        except Exception as e:
            state.status = WorkflowStatus.FAILED
            state.error = str(e)
            logger.error(f"Workflow {workflow.id} failed: {e}")
        finally:
            state.completed_at = datetime.now()

            async with self._lock:
                self._running.pop(state.workflow_id, None)

        return state

    async def cancel(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        async with self._lock:
            state = self._running.get(workflow_id)
            if state:
                state.status = WorkflowStatus.CANCELLED
                return True
            return False

    def get_state(self, workflow_id: str) -> WorkflowState | None:
        """Get workflow state."""
        return self._running.get(workflow_id)

    async def _execute_workflow(
        self,
        workflow: WorkflowDefinition,
        state: WorkflowState,
    ) -> None:
        """Execute workflow steps."""
        # Build dependency graph
        pending = set(step.id for step in workflow.steps)
        completed: set[str] = set()

        while pending and state.status == WorkflowStatus.RUNNING:
            # Find ready steps
            ready = []
            for step in workflow.steps:
                if step.id not in pending:
                    continue
                if self._dependencies_met(step, completed):
                    ready.append(step)

            if not ready:
                if pending:
                    raise RuntimeError("Deadlock: no ready steps but pending remain")
                break

            # Execute ready steps (possibly in parallel)
            if workflow.parallel:
                tasks = [
                    self._execute_step(step, state)
                    for step in ready[: self.max_concurrent]
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                for step in ready:
                    await self._execute_step(step, state)

            # Update completion status
            for step in ready:
                step_state = state.get_step_state(step.id)
                if step_state and step_state.is_complete:
                    pending.discard(step.id)
                    completed.add(step.id)

    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow_state: WorkflowState,
    ) -> None:
        """Execute a single step."""
        step_state = StepState(step_id=step.id, step_name=step.name)
        workflow_state.add_step_state(step_state)

        try:
            step_state.started_at = datetime.now()
            step_state.status = "running"

            # Check condition
            if step.condition and not self._evaluate_condition(
                step.condition, workflow_state
            ):
                step_state.status = "skipped"
                step_state.completed_at = datetime.now()
                return

            # Prepare inputs
            inputs = self._prepare_inputs(step, workflow_state)

            # Execute
            result = await self._executor.execute(step, inputs)

            step_state.outputs = result
            step_state.status = "completed"

        except Exception as e:
            step_state.status = "failed"
            step_state.error = str(e)

            if not step.continue_on_error:
                raise
        finally:
            step_state.completed_at = datetime.now()

    def _dependencies_met(self, step: WorkflowStep, completed: set[str]) -> bool:
        """Check if step dependencies are met."""
        return all(dep in completed for dep in step.depends_on)

    def _evaluate_condition(
        self,
        condition: str,
        state: WorkflowState,
    ) -> bool:
        """Evaluate step condition."""
        # Simple condition evaluation
        try:
            context = {
                "inputs": state.inputs,
                "outputs": state.outputs,
            }
            return bool(eval(condition, {"__builtins__": {}}, context))
        except Exception:
            return True

    def _prepare_inputs(
        self,
        step: WorkflowStep,
        state: WorkflowState,
    ) -> dict[str, Any]:
        """Prepare step inputs."""
        inputs = dict(state.inputs)
        inputs.update(step.inputs)

        # Add outputs from dependencies
        for dep_id in step.depends_on:
            dep_state = state.get_step_state(dep_id)
            if dep_state and dep_state.outputs:
                inputs[f"step_{dep_id}"] = dep_state.outputs

        return inputs
