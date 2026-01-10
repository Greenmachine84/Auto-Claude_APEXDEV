"""Coder Agent.

Autonomous code generation agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Responsibilities:
- Code generation from specifications
- Implementation of features
- Code refactoring
- Test generation
"""

import logging
from typing import Any, ClassVar

from ..base import (
    AgentConfig,
    BaseAgent,
    ExecutionContext,
)
from ..base.agent_hooks import HookType
from ..types import AgentResult, AgentType, ErrorCode, ErrorResult, SuccessResult

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):
    """Autonomous code generation agent.

    The Coder agent is responsible for all code generation tasks.
    It operates with file system access, git operations, and LLM calls.

    Capabilities:
    - Read and write files
    - Generate code from specifications
    - Refactor existing code
    - Create and run tests
    - Git operations (commit, branch)

    Usage:
        >>> coder = CoderAgent()
        >>> coder.initialize()
        >>> result = coder.run(context)
    """

    AGENT_TYPE: ClassVar[AgentType] = AgentType.CODER

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
    ):
        """Initialize coder agent.

        Args:
            config: Agent configuration
            agent_id: Optional agent identifier
        """
        if config is None:
            config = AgentConfig.for_coder()
        super().__init__(config=config, agent_id=agent_id)

        # Coder-specific state
        self._generated_files: list[str] = []
        self._modified_files: list[str] = []
        self._test_results: dict[str, Any] = {}

    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Autonomous code generation agent responsible for implementing "
            "features, generating tests, and refactoring code according to "
            "specifications."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute code generation task.

        Args:
            context: Execution context with task details

        Returns:
            AgentResult indicating outcome
        """
        self._logger.info(f"Coder executing task: {context.task}")

        try:
            # Emit task start hook
            self._hooks.execute(
                HookType.ON_TASK_START,
                metadata={"task_id": context.task.task_id if context.task else None},
            )

            # Core execution logic
            # In production, this integrates with LLM and file system
            result_data = self._execute_coding_task(context)

            # Emit task complete hook
            self._hooks.execute(
                HookType.ON_TASK_COMPLETE,
                result=result_data,
            )

            return SuccessResult(
                data=result_data,
                message="Code generation completed successfully",
                metadata={
                    "generated_files": self._generated_files,
                    "modified_files": self._modified_files,
                },
            )

        except Exception as e:
            self._logger.error(f"Coder execution failed: {e}")
            return ErrorResult(
                message=str(e),
                code=ErrorCode.EXECUTION_ERROR,
                recoverable=True,
            )

    def _execute_coding_task(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute the actual coding task.

        This is the core implementation that would integrate with:
        - LLM for code generation
        - File system for reading/writing
        - Git for version control

        Args:
            context: Execution context

        Returns:
            Result data dictionary
        """
        # Placeholder for actual implementation
        # In production, this calls the LLM and performs file operations
        return {
            "status": "completed",
            "task_id": context.task.task_id if context.task else None,
            "agent_id": self.id,
        }

    def generate_code(
        self,
        specification: str,
        target_file: str,
        context: ExecutionContext,
    ) -> str:
        """Generate code from specification.

        Args:
            specification: Code specification
            target_file: Target file path
            context: Execution context

        Returns:
            Generated code
        """
        # Placeholder - in production this calls LLM
        self._generated_files.append(target_file)
        return f"# Generated for: {specification}"

    def refactor_code(
        self,
        source_file: str,
        instructions: str,
        context: ExecutionContext,
    ) -> str:
        """Refactor existing code.

        Args:
            source_file: Source file to refactor
            instructions: Refactoring instructions
            context: Execution context

        Returns:
            Refactored code
        """
        self._modified_files.append(source_file)
        return f"# Refactored: {instructions}"

    def generate_tests(
        self,
        target_module: str,
        context: ExecutionContext,
    ) -> str:
        """Generate tests for a module.

        Args:
            target_module: Module to generate tests for
            context: Execution context

        Returns:
            Generated test code
        """
        test_file = f"test_{target_module}.py"
        self._generated_files.append(test_file)
        return f"# Tests for: {target_module}"

    def get_stats(self) -> dict[str, Any]:
        """Get coder statistics."""
        return {
            **self.to_dict(),
            "generated_files_count": len(self._generated_files),
            "modified_files_count": len(self._modified_files),
            "test_results": self._test_results,
        }
