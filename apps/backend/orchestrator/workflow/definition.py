"""Workflow definition.

Defines workflow structure.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowStep:
    """A step in a workflow.

    Attributes:
        id: Unique step identifier
        name: Human-readable name
        type: Step type for routing
        inputs: Step input parameters
        depends_on: Step dependencies
    """

    name: str
    type: str

    # Identification
    id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")

    # Configuration
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: list[str] = field(default_factory=list)

    # Dependencies
    depends_on: list[str] = field(default_factory=list)

    # Execution control
    condition: str | None = None
    timeout: float = 300.0
    retries: int = 0
    continue_on_error: bool = False

    # Metadata
    description: str | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "depends_on": self.depends_on,
            "condition": self.condition,
            "timeout": self.timeout,
            "retries": self.retries,
            "continue_on_error": self.continue_on_error,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowStep":
        """Create from dictionary."""
        return cls(
            id=data.get("id", f"step_{uuid.uuid4().hex[:8]}"),
            name=data["name"],
            type=data["type"],
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", []),
            depends_on=data.get("depends_on", []),
            condition=data.get("condition"),
            timeout=data.get("timeout", 300.0),
            retries=data.get("retries", 0),
            continue_on_error=data.get("continue_on_error", False),
            description=data.get("description"),
            tags=data.get("tags", []),
        )


@dataclass
class WorkflowDefinition:
    """Workflow definition.

    Defines a complete workflow with steps.

    Example:
        workflow = WorkflowDefinition(
            name="build-and-test",
            steps=[
                WorkflowStep(name="build", type="build"),
                WorkflowStep(name="test", type="test", depends_on=["build"]),
            ]
        )
    """

    name: str
    steps: list[WorkflowStep]

    # Identification
    id: str = field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    version: str = "1.0.0"

    # Configuration
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: list[str] = field(default_factory=list)

    # Execution control
    parallel: bool = False
    max_parallel: int = 4
    timeout: float = 3600.0

    # Metadata
    description: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate workflow."""
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """Validate step dependencies."""
        step_ids = {step.id for step in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(f"Step {step.id} depends on unknown step {dep}")

    def get_step(self, step_id: str) -> WorkflowStep | None:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_root_steps(self) -> list[WorkflowStep]:
        """Get steps with no dependencies."""
        return [s for s in self.steps if not s.depends_on]

    def get_leaf_steps(self) -> list[WorkflowStep]:
        """Get steps with no dependents."""
        has_dependents = set()
        for step in self.steps:
            has_dependents.update(step.depends_on)

        return [s for s in self.steps if s.id not in has_dependents]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "steps": [s.to_dict() for s in self.steps],
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parallel": self.parallel,
            "max_parallel": self.max_parallel,
            "timeout": self.timeout,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowDefinition":
        """Create from dictionary."""
        steps = [WorkflowStep.from_dict(s) for s in data.get("steps", [])]

        return cls(
            id=data.get("id", f"wf_{uuid.uuid4().hex[:12]}"),
            name=data["name"],
            version=data.get("version", "1.0.0"),
            steps=steps,
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", []),
            parallel=data.get("parallel", False),
            max_parallel=data.get("max_parallel", 4),
            timeout=data.get("timeout", 3600.0),
            description=data.get("description"),
            tags=data.get("tags", []),
        )
