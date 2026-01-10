"""Abstract base class for all skills.

Provides the foundation for skill implementation with:
- Lifecycle hooks (pre/post execute)
- Input/output validation
- Dependency management
- Tool requirements declaration
- APEX Constitution compliance

Example:
    class CodeGenerationSkill(BaseSkill):
        name = "code_generation"
        description = "Generate code from specifications"
        category = SkillCategory.CODING
        required_tools = ["file_write", "file_read"]

        async def execute(self, context: SkillContext) -> SkillResult:
            # Implementation
            pass
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from skills.types.result_types import SkillResult
    from skills.types.skill_types import SkillCategory, SkillStatus

logger = logging.getLogger(__name__)


class SkillCategory(Enum):
    """Categories of skills."""

    CODING = "coding"
    TESTING = "testing"
    REVIEW = "review"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    CUSTOM = "custom"


class SkillStatus(Enum):
    """Skill execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class SkillContext:
    """Context passed to skill execution.

    Provides all necessary information and resources for skill execution.
    """

    task_id: str
    input_data: dict[str, Any]
    memory_context: dict[str, Any] | None = None
    agent_id: str | None = None
    session_id: str | None = None
    timeout_seconds: int = 300
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_memory(self) -> bool:
        """Check if memory context is available."""
        return self.memory_context is not None


@dataclass
class SkillResult:
    """Result from skill execution."""

    skill_name: str
    status: SkillStatus
    output: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if skill completed successfully."""
        return self.status == SkillStatus.COMPLETED

    @property
    def duration_seconds(self) -> float | None:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "skill_name": self.skill_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "tokens_used": self.tokens_used,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


class BaseSkill(ABC):
    """Abstract base class for all skills.

    Skills are reusable capability units that agents use to accomplish tasks.
    Each skill encapsulates a specific capability (e.g., code generation,
    test execution, code review) with well-defined inputs and outputs.

    Attributes:
        name: Unique identifier for the skill
        description: Human-readable description
        category: Skill category (coding, testing, etc.)
        required_tools: List of tools needed by this skill
        required_permissions: Set of permissions required
        version: Skill version string
    """

    # Class-level attributes (override in subclasses)
    name: str = "base_skill"
    description: str = "Base skill - override in subclass"
    category: SkillCategory = SkillCategory.CUSTOM
    required_tools: list[str] = []
    required_permissions: set[str] = set()
    version: str = "1.0.0"

    def __init__(self) -> None:
        """Initialize the skill."""
        self._status = SkillStatus.PENDING
        self._current_context: SkillContext | None = None
        self._execution_count = 0
        self._total_tokens = 0
        self._hooks: dict[str, list[callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_error": [],
        }

    @property
    def status(self) -> SkillStatus:
        """Current execution status."""
        return self._status

    @property
    def execution_count(self) -> int:
        """Number of times this skill has been executed."""
        return self._execution_count

    def add_hook(self, hook_type: str, callback: callable) -> None:
        """Add a lifecycle hook.

        Args:
            hook_type: One of 'pre_execute', 'post_execute', 'on_error'
            callback: Async callable to invoke
        """
        if hook_type in self._hooks:
            self._hooks[hook_type].append(callback)

    async def _run_hooks(self, hook_type: str, *args, **kwargs) -> None:
        """Run all hooks of a given type."""
        for hook in self._hooks.get(hook_type, []):
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(*args, **kwargs)
                else:
                    hook(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Hook {hook_type} failed: {e}")

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data before execution.

        Override to add custom validation logic.

        Args:
            input_data: Input data dictionary

        Returns:
            True if valid, False otherwise
        """
        return True

    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validate output data after execution.

        Override to add custom validation logic.

        Args:
            output: Output data dictionary

        Returns:
            True if valid, False otherwise
        """
        return True

    def get_dependencies(self) -> list[str]:
        """Get list of skill dependencies.

        Override to declare dependencies on other skills.

        Returns:
            List of skill names this skill depends on
        """
        return []

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get tool definitions for LLM function calling.

        Returns:
            List of tool definitions in OpenAI function format
        """
        return []

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute the skill.

        Main entry point for skill execution. Must be overridden by subclasses.

        Args:
            context: Execution context with input data and resources

        Returns:
            SkillResult with output or error
        """
        pass

    async def run(self, context: SkillContext) -> SkillResult:
        """Run the skill with full lifecycle management.

        Handles:
        - Input validation
        - Pre-execution hooks
        - Execution with timeout
        - Post-execution hooks
        - Error handling
        - Output validation

        Args:
            context: Execution context

        Returns:
            SkillResult with output or error
        """
        self._current_context = context
        started_at = datetime.utcnow()

        # Validate input
        if not self.validate_input(context.input_data):
            return SkillResult(
                skill_name=self.name,
                status=SkillStatus.FAILED,
                error="Input validation failed",
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        try:
            # Pre-execution hooks
            self._status = SkillStatus.RUNNING
            await self._run_hooks("pre_execute", context)

            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(context), timeout=context.timeout_seconds
            )

            # Update result timestamps
            result.started_at = started_at
            result.completed_at = datetime.utcnow()

            # Validate output
            if result.output and not self.validate_output(result.output):
                result.status = SkillStatus.FAILED
                result.error = "Output validation failed"

            # Post-execution hooks
            await self._run_hooks("post_execute", result)

            self._status = result.status
            self._execution_count += 1
            self._total_tokens += result.tokens_used

            return result

        except asyncio.TimeoutError:
            self._status = SkillStatus.TIMEOUT
            return SkillResult(
                skill_name=self.name,
                status=SkillStatus.TIMEOUT,
                error=f"Skill timed out after {context.timeout_seconds}s",
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            self._status = SkillStatus.FAILED
            await self._run_hooks("on_error", e)
            logger.error(f"Skill {self.name} failed: {e}")
            return SkillResult(
                skill_name=self.name,
                status=SkillStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        finally:
            self._current_context = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, category={self.category.value})"
