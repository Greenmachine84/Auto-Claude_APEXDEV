"""
Integration tests for Skill Orchestration.

Tests the complete flow of skill discovery, composition, execution,
and result aggregation across multiple skills.
"""

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from unittest.mock import AsyncMock, MagicMock
import asyncio


class SkillCategory(Enum):
    """Categories of skills."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_REFACTOR = "code_refactor"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"


class SkillPriority(Enum):
    """Skill execution priority."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class CompositionMode(Enum):
    """How skills are composed together."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"


@dataclass
class SkillResult:
    """Result from skill execution."""
    skill_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class SkillContext:
    """Context for skill execution."""
    task_id: str
    input_data: Any
    variables: dict = field(default_factory=dict)
    previous_results: list[SkillResult] = field(default_factory=list)

    def get_last_output(self) -> Any:
        """Get output from the last executed skill."""
        if self.previous_results:
            return self.previous_results[-1].output
        return self.input_data


@dataclass
class SkillDefinition:
    """Definition of a skill."""
    id: str
    name: str
    category: SkillCategory
    priority: SkillPriority = SkillPriority.NORMAL
    handler: Optional[Callable] = None
    dependencies: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    timeout_seconds: float = 60.0
    retryable: bool = True
    max_retries: int = 3


class MockSkill:
    """Mock skill implementation."""

    def __init__(self, definition: SkillDefinition):
        self.definition = definition
        self.execution_count = 0
        self._results: list[SkillResult] = []
        self._should_fail = False
        self._delay_seconds = 0.0

    def set_results(self, results: list[SkillResult]) -> None:
        """Set predefined results."""
        self._results = results.copy()

    def set_failure_mode(self, should_fail: bool) -> None:
        """Configure failure behavior."""
        self._should_fail = should_fail

    def set_delay(self, delay_seconds: float) -> None:
        """Set execution delay."""
        self._delay_seconds = delay_seconds

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute the skill."""
        self.execution_count += 1

        if self._delay_seconds > 0:
            await asyncio.sleep(self._delay_seconds)

        if self._should_fail:
            return SkillResult(
                skill_id=self.definition.id,
                success=False,
                error=f"Skill {self.definition.id} failed"
            )

        if self._results:
            return self._results.pop(0)

        if self.definition.handler:
            try:
                output = self.definition.handler(context)
                return SkillResult(
                    skill_id=self.definition.id,
                    success=True,
                    output=output
                )
            except Exception as e:
                return SkillResult(
                    skill_id=self.definition.id,
                    success=False,
                    error=str(e)
                )

        return SkillResult(
            skill_id=self.definition.id,
            success=True,
            output=f"Executed {self.definition.name}"
        )


class MockSkillRegistry:
    """Registry for available skills."""

    def __init__(self):
        self._skills: dict[str, MockSkill] = {}
        self._category_index: dict[SkillCategory, list[str]] = {}

    def register(self, skill: MockSkill) -> None:
        """Register a skill."""
        self._skills[skill.definition.id] = skill
        category = skill.definition.category
        if category not in self._category_index:
            self._category_index[category] = []
        self._category_index[category].append(skill.definition.id)

    def get(self, skill_id: str) -> MockSkill:
        """Get a skill by ID."""
        if skill_id not in self._skills:
            raise KeyError(f"Skill {skill_id} not found")
        return self._skills[skill_id]

    def get_by_category(self, category: SkillCategory) -> list[MockSkill]:
        """Get skills by category."""
        skill_ids = self._category_index.get(category, [])
        return [self._skills[sid] for sid in skill_ids]

    def list_all(self) -> list[str]:
        """List all skill IDs."""
        return list(self._skills.keys())


@dataclass
class SkillPipeline:
    """Pipeline definition for skill composition."""
    id: str
    name: str
    mode: CompositionMode
    skill_ids: list[str] = field(default_factory=list)
    conditions: dict[str, Callable[[SkillContext], bool]] = field(default_factory=dict)

    def add_skill(
        self,
        skill_id: str,
        condition: Optional[Callable[[SkillContext], bool]] = None
    ) -> None:
        """Add a skill to the pipeline."""
        self.skill_ids.append(skill_id)
        if condition:
            self.conditions[skill_id] = condition


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    pipeline_id: str
    success: bool
    results: list[SkillResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    error: Optional[str] = None


class MockSkillOrchestrator:
    """Orchestrator for skill execution and composition."""

    def __init__(self, registry: MockSkillRegistry):
        self.registry = registry
        self.execution_history: list[SkillResult] = []
        self._event_handlers: dict[str, list[Callable]] = {}

    def on_event(self, event: str, handler: Callable) -> None:
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit(self, event: str, data: Any) -> None:
        """Emit an event."""
        for handler in self._event_handlers.get(event, []):
            handler(data)

    async def execute_skill(
        self,
        skill_id: str,
        context: SkillContext
    ) -> SkillResult:
        """Execute a single skill."""
        skill = self.registry.get(skill_id)
        self._emit("skill_started", {"skill_id": skill_id})

        result = await skill.execute(context)
        context.previous_results.append(result)
        self.execution_history.append(result)

        self._emit("skill_completed", {"skill_id": skill_id, "result": result})
        return result

    async def execute_pipeline(
        self,
        pipeline: SkillPipeline,
        initial_context: SkillContext
    ) -> PipelineResult:
        """Execute a skill pipeline."""
        self._emit("pipeline_started", {"pipeline_id": pipeline.id})

        import time
        start_time = time.time()

        results: list[SkillResult] = []
        context = initial_context

        try:
            if pipeline.mode == CompositionMode.SEQUENTIAL:
                results = await self._execute_sequential(pipeline, context)
            elif pipeline.mode == CompositionMode.PARALLEL:
                results = await self._execute_parallel(pipeline, context)
            elif pipeline.mode == CompositionMode.CONDITIONAL:
                results = await self._execute_conditional(pipeline, context)
            elif pipeline.mode == CompositionMode.PIPELINE:
                results = await self._execute_pipeline_mode(pipeline, context)

            success = all(r.success for r in results)
            error = None
            if not success:
                failed = [r for r in results if not r.success]
                error = f"{len(failed)} skill(s) failed"

        except Exception as e:
            success = False
            error = str(e)

        duration = (time.time() - start_time) * 1000

        pipeline_result = PipelineResult(
            pipeline_id=pipeline.id,
            success=success,
            results=results,
            total_duration_ms=duration,
            error=error
        )

        self._emit("pipeline_completed", {
            "pipeline_id": pipeline.id,
            "result": pipeline_result
        })

        return pipeline_result

    async def _execute_sequential(
        self,
        pipeline: SkillPipeline,
        context: SkillContext
    ) -> list[SkillResult]:
        """Execute skills sequentially."""
        results = []
        for skill_id in pipeline.skill_ids:
            result = await self.execute_skill(skill_id, context)
            results.append(result)
            if not result.success:
                break
        return results

    async def _execute_parallel(
        self,
        pipeline: SkillPipeline,
        context: SkillContext
    ) -> list[SkillResult]:
        """Execute skills in parallel."""
        tasks = []
        for skill_id in pipeline.skill_ids:
            # Create separate context for each parallel skill
            skill_context = SkillContext(
                task_id=context.task_id,
                input_data=context.input_data,
                variables=context.variables.copy()
            )
            tasks.append(self.execute_skill(skill_id, skill_context))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            r if isinstance(r, SkillResult)
            else SkillResult(skill_id="unknown", success=False, error=str(r))
            for r in results
        ]

    async def _execute_conditional(
        self,
        pipeline: SkillPipeline,
        context: SkillContext
    ) -> list[SkillResult]:
        """Execute skills based on conditions."""
        results = []
        for skill_id in pipeline.skill_ids:
            condition = pipeline.conditions.get(skill_id)
            if condition is None or condition(context):
                result = await self.execute_skill(skill_id, context)
                results.append(result)
        return results

    async def _execute_pipeline_mode(
        self,
        pipeline: SkillPipeline,
        context: SkillContext
    ) -> list[SkillResult]:
        """Execute skills in pipeline mode (output -> input)."""
        results = []
        current_data = context.input_data

        for skill_id in pipeline.skill_ids:
            pipe_context = SkillContext(
                task_id=context.task_id,
                input_data=current_data,
                variables=context.variables,
                previous_results=results.copy()
            )
            result = await self.execute_skill(skill_id, pipe_context)
            results.append(result)

            if not result.success:
                break
            current_data = result.output

        return results


# ============================================================================
# Test Classes
# ============================================================================

class TestSkillDiscovery:
    """Tests for skill discovery and registration."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create skill registry with skills."""
        registry = MockSkillRegistry()
        for category in [SkillCategory.CODE_GENERATION, SkillCategory.CODE_REVIEW]:
            for i in range(3):
                skill = MockSkill(SkillDefinition(
                    id=f"{category.value}_{i}",
                    name=f"{category.value} Skill {i}",
                    category=category
                ))
                registry.register(skill)
        return registry

    def test_list_all_skills(self, registry: MockSkillRegistry):
        """Test listing all registered skills."""
        skills = registry.list_all()
        assert len(skills) == 6

    def test_get_by_category(self, registry: MockSkillRegistry):
        """Test getting skills by category."""
        code_gen = registry.get_by_category(SkillCategory.CODE_GENERATION)
        assert len(code_gen) == 3

    def test_get_unknown_skill(self, registry: MockSkillRegistry):
        """Test getting unknown skill raises error."""
        with pytest.raises(KeyError):
            registry.get("unknown_skill")


class TestSequentialExecution:
    """Tests for sequential skill execution."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry with sequential skills."""
        registry = MockSkillRegistry()
        for i in range(3):
            skill = MockSkill(SkillDefinition(
                id=f"step_{i}",
                name=f"Step {i}",
                category=SkillCategory.ANALYSIS
            ))
            registry.register(skill)
        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_sequential_execution(self, orchestrator: MockSkillOrchestrator):
        """Test skills execute in sequence."""
        pipeline = SkillPipeline(
            id="seq-pipeline",
            name="Sequential Pipeline",
            mode=CompositionMode.SEQUENTIAL,
            skill_ids=["step_0", "step_1", "step_2"]
        )
        context = SkillContext(task_id="test", input_data="input")

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is True
        assert len(result.results) == 3

    @pytest.mark.asyncio
    async def test_sequential_stops_on_failure(
        self,
        orchestrator: MockSkillOrchestrator,
        registry: MockSkillRegistry
    ):
        """Test sequential execution stops on failure."""
        registry.get("step_1").set_failure_mode(True)

        pipeline = SkillPipeline(
            id="fail-pipeline",
            name="Failing Pipeline",
            mode=CompositionMode.SEQUENTIAL,
            skill_ids=["step_0", "step_1", "step_2"]
        )
        context = SkillContext(task_id="test", input_data="input")

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is False
        assert len(result.results) == 2  # Stopped after step_1


class TestParallelExecution:
    """Tests for parallel skill execution."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry with parallel skills."""
        registry = MockSkillRegistry()
        for i in range(3):
            skill = MockSkill(SkillDefinition(
                id=f"parallel_{i}",
                name=f"Parallel {i}",
                category=SkillCategory.ANALYSIS
            ))
            skill.set_delay(0.01)  # Small delay
            registry.register(skill)
        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator: MockSkillOrchestrator):
        """Test skills execute in parallel."""
        pipeline = SkillPipeline(
            id="parallel-pipeline",
            name="Parallel Pipeline",
            mode=CompositionMode.PARALLEL,
            skill_ids=["parallel_0", "parallel_1", "parallel_2"]
        )
        context = SkillContext(task_id="test", input_data="input")

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is True
        assert len(result.results) == 3

    @pytest.mark.asyncio
    async def test_parallel_partial_failure(
        self,
        orchestrator: MockSkillOrchestrator,
        registry: MockSkillRegistry
    ):
        """Test parallel execution continues despite failures."""
        registry.get("parallel_1").set_failure_mode(True)

        pipeline = SkillPipeline(
            id="partial-fail",
            name="Partial Fail",
            mode=CompositionMode.PARALLEL,
            skill_ids=["parallel_0", "parallel_1", "parallel_2"]
        )
        context = SkillContext(task_id="test", input_data="input")

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is False
        assert len(result.results) == 3  # All attempted


class TestConditionalExecution:
    """Tests for conditional skill execution."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry with conditional skills."""
        registry = MockSkillRegistry()
        for name in ["always", "when_flag", "when_high"]:
            skill = MockSkill(SkillDefinition(
                id=name,
                name=name,
                category=SkillCategory.ANALYSIS
            ))
            registry.register(skill)
        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_conditional_execution(self, orchestrator: MockSkillOrchestrator):
        """Test skills execute based on conditions."""
        pipeline = SkillPipeline(
            id="cond-pipeline",
            name="Conditional Pipeline",
            mode=CompositionMode.CONDITIONAL,
            skill_ids=["always", "when_flag", "when_high"]
        )
        pipeline.conditions["when_flag"] = lambda ctx: ctx.variables.get("flag", False)
        pipeline.conditions["when_high"] = lambda ctx: ctx.variables.get("level", 0) > 50

        context = SkillContext(
            task_id="test",
            input_data="input",
            variables={"flag": True, "level": 30}
        )

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is True
        executed_ids = [r.skill_id for r in result.results]
        assert "always" in executed_ids
        assert "when_flag" in executed_ids
        assert "when_high" not in executed_ids


class TestPipelineMode:
    """Tests for pipeline mode (output -> input)."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry with pipeline skills."""
        registry = MockSkillRegistry()

        # Skill that doubles input
        double = MockSkill(SkillDefinition(
            id="double",
            name="Double",
            category=SkillCategory.ANALYSIS,
            handler=lambda ctx: ctx.input_data * 2
        ))
        registry.register(double)

        # Skill that adds 10
        add_ten = MockSkill(SkillDefinition(
            id="add_ten",
            name="Add Ten",
            category=SkillCategory.ANALYSIS,
            handler=lambda ctx: ctx.input_data + 10
        ))
        registry.register(add_ten)

        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_pipeline_data_flow(self, orchestrator: MockSkillOrchestrator):
        """Test data flows through pipeline."""
        pipeline = SkillPipeline(
            id="math-pipeline",
            name="Math Pipeline",
            mode=CompositionMode.PIPELINE,
            skill_ids=["double", "add_ten"]
        )
        context = SkillContext(task_id="test", input_data=5)

        result = await orchestrator.execute_pipeline(pipeline, context)

        assert result.success is True
        # 5 * 2 = 10, 10 + 10 = 20
        assert result.results[-1].output == 20


class TestSkillEvents:
    """Tests for skill orchestration events."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry."""
        registry = MockSkillRegistry()
        skill = MockSkill(SkillDefinition(
            id="test_skill",
            name="Test Skill",
            category=SkillCategory.ANALYSIS
        ))
        registry.register(skill)
        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_events_emitted(self, orchestrator: MockSkillOrchestrator):
        """Test events are emitted during execution."""
        events = []

        orchestrator.on_event("skill_started", lambda d: events.append(("started", d)))
        orchestrator.on_event("skill_completed", lambda d: events.append(("completed", d)))

        context = SkillContext(task_id="test", input_data="input")
        await orchestrator.execute_skill("test_skill", context)

        assert len(events) == 2
        assert events[0][0] == "started"
        assert events[1][0] == "completed"


class TestExecutionHistory:
    """Tests for execution history tracking."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry."""
        registry = MockSkillRegistry()
        for i in range(5):
            skill = MockSkill(SkillDefinition(
                id=f"hist_{i}",
                name=f"History {i}",
                category=SkillCategory.ANALYSIS
            ))
            registry.register(skill)
        return registry

    @pytest.fixture
    def orchestrator(self, registry: MockSkillRegistry) -> MockSkillOrchestrator:
        """Create orchestrator."""
        return MockSkillOrchestrator(registry)

    @pytest.mark.asyncio
    async def test_history_tracked(self, orchestrator: MockSkillOrchestrator):
        """Test execution history is tracked."""
        pipeline = SkillPipeline(
            id="hist-pipeline",
            name="History Pipeline",
            mode=CompositionMode.SEQUENTIAL,
            skill_ids=["hist_0", "hist_1", "hist_2"]
        )
        context = SkillContext(task_id="test", input_data="input")

        await orchestrator.execute_pipeline(pipeline, context)

        assert len(orchestrator.execution_history) == 3
        assert [r.skill_id for r in orchestrator.execution_history] == ["hist_0", "hist_1", "hist_2"]


class TestSkillDependencies:
    """Tests for skill dependency resolution."""

    @pytest.fixture
    def registry(self) -> MockSkillRegistry:
        """Create registry with dependent skills."""
        registry = MockSkillRegistry()

        base = MockSkill(SkillDefinition(
            id="base",
            name="Base Skill",
            category=SkillCategory.ANALYSIS
        ))
        registry.register(base)

        dependent = MockSkill(SkillDefinition(
            id="dependent",
            name="Dependent Skill",
            category=SkillCategory.ANALYSIS,
            dependencies=["base"]
        ))
        registry.register(dependent)

        return registry

    def test_dependencies_defined(self, registry: MockSkillRegistry):
        """Test skill dependencies are defined."""
        dependent = registry.get("dependent")
        assert "base" in dependent.definition.dependencies

    def test_base_has_no_dependencies(self, registry: MockSkillRegistry):
        """Test base skill has no dependencies."""
        base = registry.get("base")
        assert len(base.definition.dependencies) == 0
