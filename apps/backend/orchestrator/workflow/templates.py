"""Workflow templates.

Pre-defined workflow templates.

Provides:
- Common patterns
- Reusable workflows
- Template customization
"""

from typing import Any, Dict, List, Optional

from orchestrator.workflow.definition import WorkflowDefinition, WorkflowStep


class WorkflowTemplates:
    """Pre-defined workflow templates.
    
    Example:
        templates = WorkflowTemplates()
        workflow = templates.create("build-test-deploy")
    """
    
    @staticmethod
    def build_and_test(
        project_path: str,
        test_command: str = "pytest",
    ) -> WorkflowDefinition:
        """Create build and test workflow."""
        return WorkflowDefinition(
            name="build-and-test",
            description="Build and test a project",
            steps=[
                WorkflowStep(
                    id="install",
                    name="Install Dependencies",
                    type="shell",
                    inputs={"command": "pip install -r requirements.txt"},
                ),
                WorkflowStep(
                    id="lint",
                    name="Lint Code",
                    type="shell",
                    inputs={"command": "ruff check ."},
                    depends_on=["install"],
                    continue_on_error=True,
                ),
                WorkflowStep(
                    id="test",
                    name="Run Tests",
                    type="shell",
                    inputs={"command": test_command},
                    depends_on=["install"],
                ),
            ],
            inputs={"project_path": project_path},
        )
    
    @staticmethod
    def code_review(
        files: List[str],
        review_type: str = "comprehensive",
    ) -> WorkflowDefinition:
        """Create code review workflow."""
        return WorkflowDefinition(
            name="code-review",
            description="Review code files",
            parallel=True,
            steps=[
                WorkflowStep(
                    id="analyze",
                    name="Static Analysis",
                    type="analyze",
                    inputs={"files": files},
                ),
                WorkflowStep(
                    id="security",
                    name="Security Scan",
                    type="security_scan",
                    inputs={"files": files},
                ),
                WorkflowStep(
                    id="review",
                    name="AI Review",
                    type="ai_review",
                    inputs={"files": files, "type": review_type},
                    depends_on=["analyze", "security"],
                ),
                WorkflowStep(
                    id="report",
                    name="Generate Report",
                    type="report",
                    depends_on=["review"],
                ),
            ],
            inputs={"files": files},
        )
    
    @staticmethod
    def pipeline(
        stages: List[Dict[str, Any]],
    ) -> WorkflowDefinition:
        """Create custom pipeline workflow."""
        steps = []
        prev_id = None
        
        for i, stage in enumerate(stages):
            step = WorkflowStep(
                id=stage.get("id", f"stage_{i}"),
                name=stage.get("name", f"Stage {i}"),
                type=stage.get("type", "shell"),
                inputs=stage.get("inputs", {}),
                depends_on=[prev_id] if prev_id else [],
            )
            steps.append(step)
            prev_id = step.id
        
        return WorkflowDefinition(
            name="custom-pipeline",
            description="Custom pipeline workflow",
            steps=steps,
        )
    
    @staticmethod
    def parallel_tasks(
        tasks: List[Dict[str, Any]],
        final_step: Optional[Dict[str, Any]] = None,
    ) -> WorkflowDefinition:
        """Create parallel tasks workflow."""
        steps = []
        task_ids = []
        
        for i, task in enumerate(tasks):
            step = WorkflowStep(
                id=task.get("id", f"task_{i}"),
                name=task.get("name", f"Task {i}"),
                type=task.get("type", "shell"),
                inputs=task.get("inputs", {}),
            )
            steps.append(step)
            task_ids.append(step.id)
        
        if final_step:
            steps.append(WorkflowStep(
                id=final_step.get("id", "final"),
                name=final_step.get("name", "Final"),
                type=final_step.get("type", "shell"),
                inputs=final_step.get("inputs", {}),
                depends_on=task_ids,
            ))
        
        return WorkflowDefinition(
            name="parallel-tasks",
            description="Parallel tasks with optional final step",
            steps=steps,
            parallel=True,
        )
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> WorkflowDefinition:
        """Create workflow from template dictionary."""
        return WorkflowDefinition.from_dict(data)
