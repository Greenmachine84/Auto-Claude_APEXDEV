"""Pipeline manager for orchestration.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StageStatus(str, Enum):
    """Status of a pipeline stage."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """A stage in a pipeline."""

    stage_id: str
    name: str
    agent_id: str
    action: str = "execute"  # Method to call on agent
    depends_on: list[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: float = 60.0
    condition: str | None = None  # Condition for execution
    transform_input: Callable | None = None
    transform_output: Callable | None = None
    status: StageStatus = StageStatus.PENDING
    result: Any | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage_id": self.stage_id,
            "name": self.name,
            "agent_id": self.agent_id,
            "action": self.action,
            "depends_on": self.depends_on,
            "retry_count": self.retry_count,
            "timeout": self.timeout,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class Pipeline:
    """An execution pipeline."""

    pipeline_id: str
    name: str
    description: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline."""
        self.stages.append(stage)

    def get_stage(self, stage_id: str) -> PipelineStage | None:
        """Get a stage by ID."""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "stages": [s.to_dict() for s in self.stages],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class PipelineExecutionResult:
    """Result of pipeline execution."""

    success: bool = True
    stages_completed: int = 0
    stages_failed: int = 0
    stage_results: dict[str, Any] = field(default_factory=dict)
    final_output: Any | None = None
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class PipelineManager:
    """Manages and executes pipelines.

    Handles pipeline registration, execution,
    and result tracking.
    """

    def __init__(self):
        """Initialize manager."""
        self._pipelines: dict[str, Pipeline] = {}

    def create_pipeline(
        self,
        pipeline_id: str,
        name: str,
        description: str = "",
        stages: list[dict[str, Any]] | None = None,
    ) -> Pipeline:
        """Create and register a new pipeline.

        Args:
            pipeline_id: Unique pipeline identifier
            name: Pipeline name
            description: Pipeline description
            stages: List of stage configurations

        Returns:
            Created pipeline
        """
        pipeline = Pipeline(
            pipeline_id=pipeline_id,
            name=name,
            description=description,
        )

        if stages:
            for stage_config in stages:
                stage = PipelineStage(
                    stage_id=stage_config.get(
                        "stage_id", f"stage_{len(pipeline.stages)}"
                    ),
                    name=stage_config.get("name", "Unnamed Stage"),
                    agent_id=stage_config.get("agent_id", ""),
                    action=stage_config.get("action", "execute"),
                    depends_on=stage_config.get("depends_on", []),
                    retry_count=stage_config.get("retry_count", 3),
                    timeout=stage_config.get("timeout", 60.0),
                    condition=stage_config.get("condition"),
                )
                pipeline.add_stage(stage)

        self._pipelines[pipeline_id] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> Pipeline | None:
        """Get a pipeline by ID."""
        return self._pipelines.get(pipeline_id)

    def list_pipelines(self) -> list[Pipeline]:
        """List all registered pipelines."""
        return list(self._pipelines.values())

    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return True
        return False

    async def execute(
        self,
        pipeline: Pipeline,
        context: dict[str, Any],
        agents: dict[str, Any],
    ) -> PipelineExecutionResult:
        """Execute a pipeline.

        Args:
            pipeline: Pipeline to execute
            context: Initial context
            agents: Available agents

        Returns:
            Execution result
        """
        start_time = datetime.now()
        result = PipelineExecutionResult()

        # Build execution order
        execution_order = self._resolve_dependencies(pipeline)

        current_context = context.copy()

        for stage in execution_order:
            # Check if dependencies succeeded
            deps_ok = all(
                pipeline.get_stage(dep_id).status == StageStatus.COMPLETED
                for dep_id in stage.depends_on
                if pipeline.get_stage(dep_id)
            )

            if not deps_ok:
                stage.status = StageStatus.SKIPPED
                continue

            # Check condition
            if stage.condition:
                if not self._evaluate_condition(stage.condition, current_context):
                    stage.status = StageStatus.SKIPPED
                    continue

            # Execute stage
            stage.status = StageStatus.RUNNING

            agent = agents.get(stage.agent_id)
            if not agent:
                stage.status = StageStatus.FAILED
                stage.error = f"Agent '{stage.agent_id}' not found"
                result.errors.append(stage.error)
                result.stages_failed += 1
                continue

            # Execute with retries
            success = False
            for attempt in range(stage.retry_count):
                try:
                    # Transform input if needed
                    stage_context = current_context
                    if stage.transform_input:
                        stage_context = stage.transform_input(current_context)

                    # Execute with timeout
                    stage_result = await asyncio.wait_for(
                        self._execute_stage(agent, stage.action, stage_context),
                        timeout=stage.timeout,
                    )

                    # Transform output if needed
                    if stage.transform_output:
                        stage_result = stage.transform_output(stage_result)

                    stage.result = stage_result
                    stage.status = StageStatus.COMPLETED
                    result.stage_results[stage.stage_id] = stage_result
                    result.stages_completed += 1

                    # Update context
                    current_context[stage.stage_id] = stage_result

                    success = True
                    break

                except asyncio.TimeoutError:
                    stage.error = f"Timeout after {stage.timeout}s"
                except Exception as e:
                    stage.error = str(e)

            if not success:
                stage.status = StageStatus.FAILED
                result.errors.append(f"{stage.stage_id}: {stage.error}")
                result.stages_failed += 1

        # Determine success and final output
        result.success = result.stages_failed == 0

        # Use last completed stage result as final output
        for stage in reversed(execution_order):
            if stage.status == StageStatus.COMPLETED:
                result.final_output = stage.result
                break

        result.execution_time = (datetime.now() - start_time).total_seconds()

        return result

    async def _execute_stage(
        self,
        agent: Any,
        action: str,
        context: dict[str, Any],
    ) -> Any:
        """Execute a single stage action."""
        method = getattr(agent, action, None)
        if method is None:
            raise ValueError(f"Agent has no method '{action}'")

        if asyncio.iscoroutinefunction(method):
            return await method(context)
        else:
            return method(context)

    def _resolve_dependencies(
        self,
        pipeline: Pipeline,
    ) -> list[PipelineStage]:
        """Resolve stage dependencies and return execution order."""
        ordered: list[PipelineStage] = []
        visited: set = set()

        def visit(stage: PipelineStage) -> None:
            if stage.stage_id in visited:
                return

            for dep_id in stage.depends_on:
                dep_stage = pipeline.get_stage(dep_id)
                if dep_stage:
                    visit(dep_stage)

            visited.add(stage.stage_id)
            ordered.append(stage)

        for stage in pipeline.stages:
            visit(stage)

        return ordered

    def _evaluate_condition(
        self,
        condition: str,
        context: dict[str, Any],
    ) -> bool:
        """Evaluate a stage condition."""
        # Simple condition evaluation
        # Format: "stage_id.field == value" or "stage_id.field exists"

        try:
            if " == " in condition:
                left, right = condition.split(" == ")
                left_value = self._get_nested_value(left.strip(), context)
                right_value = right.strip().strip("'\"")
                return str(left_value) == right_value

            elif " exists" in condition:
                field = condition.replace(" exists", "").strip()
                return self._get_nested_value(field, context) is not None

            elif " != " in condition:
                left, right = condition.split(" != ")
                left_value = self._get_nested_value(left.strip(), context)
                right_value = right.strip().strip("'\"")
                return str(left_value) != right_value

            return True

        except Exception:
            return True  # Default to executing if condition parsing fails

    def _get_nested_value(
        self,
        path: str,
        context: dict[str, Any],
    ) -> Any:
        """Get a nested value from context."""
        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def create_standard_pipelines(self) -> None:
        """Create standard enterprise pipelines."""
        # Code Review Pipeline
        self.create_pipeline(
            pipeline_id="code_review",
            name="Code Review Pipeline",
            description="Full code review with security and quality checks",
            stages=[
                {
                    "stage_id": "security_scan",
                    "name": "Security Scan",
                    "agent_id": "security",
                    "action": "scan_code",
                },
                {
                    "stage_id": "code_review",
                    "name": "Code Review",
                    "agent_id": "code_review",
                    "action": "review_file",
                    "depends_on": ["security_scan"],
                },
                {
                    "stage_id": "test_generation",
                    "name": "Test Generation",
                    "agent_id": "qa",
                    "action": "generate_tests",
                    "depends_on": ["code_review"],
                },
            ],
        )

        # Documentation Pipeline
        self.create_pipeline(
            pipeline_id="documentation",
            name="Documentation Pipeline",
            description="Generate comprehensive documentation",
            stages=[
                {
                    "stage_id": "analyze_project",
                    "name": "Analyze Project",
                    "agent_id": "project_analysis",
                    "action": "execute",
                },
                {
                    "stage_id": "generate_docs",
                    "name": "Generate Documentation",
                    "agent_id": "documentation",
                    "action": "generate_docstrings",
                    "depends_on": ["analyze_project"],
                },
            ],
        )
