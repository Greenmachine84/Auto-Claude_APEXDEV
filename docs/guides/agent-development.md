# Agent Development Guide

A comprehensive guide to developing custom agents in Auto-Claude.

## Overview

Agents are autonomous entities that combine LLM capabilities with tools,
memory, and skills to accomplish complex tasks.

## Agent Architecture

```
┌─────────────────────────────────────────┐
│                 Agent                   │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │   LLM   │  │ Memory  │  │  Tools  │ │
│  │Provider │  │  Store  │  │Registry │ │
│  └─────────┘  └─────────┘  └─────────┘ │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │            Skills                   ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │          Task Executor              ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## Creating a Basic Agent

### Step 1: Define Agent Class

```python
from apps.backend.agents import BaseAgent, AgentConfig
from apps.backend.agents.models import Task, TaskResult

class DataAnalystAgent(BaseAgent):
    """Agent for analyzing data and generating insights."""

    name = "data_analyst"
    description = "Analyzes data and provides insights"
    version = "1.0.0"

    def __init__(self, provider, config: AgentConfig = None):
        super().__init__(provider, config or AgentConfig())
        self.analysis_tools = ["pandas", "matplotlib"]

    async def execute(self, task: Task) -> TaskResult:
        """Execute a data analysis task."""
        # Plan the analysis
        plan = await self.plan(task.description)

        # Execute each step
        results = []
        for step in plan.steps:
            result = await self._execute_step(step)
            results.append(result)

        # Synthesize results
        output = await self._synthesize(results)

        return TaskResult(
            task_id=task.id,
            success=True,
            output=output
        )
```

### Step 2: Implement Core Methods

```python
class DataAnalystAgent(BaseAgent):
    # ... __init__ and execute ...

    async def plan(self, goal: str) -> ExecutionPlan:
        """Create a plan for the analysis."""
        response = await self.provider.complete([
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": f"Create an analysis plan for: {goal}"}
        ])

        return self._parse_plan(response.content)

    async def _execute_step(self, step: PlanStep) -> StepResult:
        """Execute a single analysis step."""
        if step.requires_tool:
            return await self._execute_with_tools(step)
        return await self._execute_reasoning(step)

    async def _synthesize(self, results: list[StepResult]) -> str:
        """Synthesize results into final output."""
        context = "\n".join(r.output for r in results)
        response = await self.provider.complete([
            {"role": "system", "content": "Synthesize analysis results."},
            {"role": "user", "content": context}
        ])
        return response.content

    def _get_system_prompt(self) -> str:
        return """You are a data analyst agent. Your capabilities include:
        - Data exploration and profiling
        - Statistical analysis
        - Visualization recommendations
        - Insight generation
        Always provide clear, actionable insights."""
```

### Step 3: Add Tool Integration

```python
from apps.backend.tools import ToolRegistry, ToolExecutor

class DataAnalystAgent(BaseAgent):
    def __init__(self, provider, config, tools: ToolRegistry = None):
        super().__init__(provider, config)
        self.tools = tools or self._default_tools()
        self.tool_executor = ToolExecutor(registry=self.tools)

    def _default_tools(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register_all([
            read_csv,
            write_csv,
            plot_chart,
            calculate_stats
        ])
        return registry

    async def _execute_with_tools(self, step: PlanStep) -> StepResult:
        """Execute step using tools."""
        # Get tool to use
        tool_call = await self._decide_tool(step)

        # Execute tool
        result = await self.tool_executor.execute(
            tool_name=tool_call.name,
            parameters=tool_call.parameters
        )

        return StepResult(
            step_id=step.id,
            output=result.output,
            tool_used=tool_call.name
        )
```

### Step 4: Add Memory Integration

```python
from apps.backend.memory import MemoryStore, MemoryEntry, MemoryCategory

class DataAnalystAgent(BaseAgent):
    def __init__(self, provider, config, memory: MemoryStore = None):
        super().__init__(provider, config)
        self.memory = memory

    async def execute(self, task: Task) -> TaskResult:
        # Retrieve relevant context
        if self.memory:
            context = await self._get_relevant_memories(task)
        else:
            context = []

        # ... execute task with context ...

        # Store learnings
        if self.memory and result.success:
            await self._store_learnings(task, result)

        return result

    async def _get_relevant_memories(self, task: Task) -> list[MemoryEntry]:
        return await self.memory.search_semantic(
            query=task.description,
            category=MemoryCategory.PROCEDURAL,
            limit=5
        )

    async def _store_learnings(self, task: Task, result: TaskResult):
        await self.memory.store(MemoryEntry(
            id=f"learning-{task.id}",
            content=f"Task: {task.description}\nResult: {result.output}",
            category=MemoryCategory.EPISODIC,
            metadata={"task_id": task.id, "success": result.success}
        ))
```

## Agent Configuration

### Configuration Options

```python
@dataclass
class AgentConfig:
    # LLM settings
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0

    # Execution settings
    max_iterations: int = 10
    timeout: int = 300
    retry_attempts: int = 3

    # Memory settings
    use_memory: bool = True
    memory_context_limit: int = 5

    # Tool settings
    allowed_tools: list[str] = field(default_factory=list)
    tool_timeout: int = 30

    # Logging
    verbose: bool = False
    log_level: str = "INFO"
```

### Runtime Configuration

```python
agent = DataAnalystAgent(
    provider=anthropic_provider,
    config=AgentConfig(
        max_tokens=8192,
        temperature=0.3,  # More deterministic
        max_iterations=20,
        allowed_tools=["read_csv", "calculate_stats"]
    )
)
```

## Advanced Patterns

### Multi-Step Reasoning

```python
class ReasoningAgent(BaseAgent):
    async def reason(self, question: str) -> str:
        """Multi-step reasoning with chain-of-thought."""
        thoughts = []

        # Initial analysis
        thought = await self._think("What do I know about this?", question)
        thoughts.append(thought)

        # Iterative refinement
        for i in range(self.config.max_iterations):
            thought = await self._think(
                "What else should I consider?",
                question,
                previous_thoughts=thoughts
            )
            thoughts.append(thought)

            if await self._is_conclusion_reached(thoughts):
                break

        # Synthesize conclusion
        return await self._conclude(question, thoughts)

    async def _think(self, prompt: str, context: str, 
                     previous_thoughts: list = None) -> str:
        messages = [
            {"role": "system", "content": "Think step by step."},
            {"role": "user", "content": f"{prompt}\n\nContext: {context}"}
        ]

        if previous_thoughts:
            messages.append({
                "role": "assistant",
                "content": "\n".join(previous_thoughts)
            })

        response = await self.provider.complete(messages)
        return response.content
```

### Self-Correction

```python
class SelfCorrectingAgent(BaseAgent):
    async def execute_with_validation(self, task: Task) -> TaskResult:
        """Execute with self-correction loop."""
        for attempt in range(self.config.retry_attempts):
            result = await self.execute(task)

            # Validate result
            validation = await self._validate(result)

            if validation.is_valid:
                return result

            # Self-correct
            task = await self._create_correction_task(
                original_task=task,
                result=result,
                issues=validation.issues
            )

        return TaskResult(
            task_id=task.id,
            success=False,
            error="Max correction attempts exceeded"
        )

    async def _validate(self, result: TaskResult) -> ValidationResult:
        response = await self.provider.complete([
            {"role": "system", "content": "Validate this result for correctness."},
            {"role": "user", "content": f"Result: {result.output}"}
        ])
        return self._parse_validation(response.content)
```

### Agent Collaboration

```python
class CollaborativeAgent(BaseAgent):
    def __init__(self, provider, config, collaborators: dict):
        super().__init__(provider, config)
        self.collaborators = collaborators

    async def delegate(self, subtask: Task, to: str) -> TaskResult:
        """Delegate subtask to another agent."""
        collaborator = self.collaborators.get(to)
        if not collaborator:
            raise ValueError(f"Unknown collaborator: {to}")

        return await collaborator.execute(subtask)

    async def execute(self, task: Task) -> TaskResult:
        # Plan and identify delegations
        plan = await self.plan(task)

        results = {}
        for step in plan.steps:
            if step.delegate_to:
                results[step.id] = await self.delegate(
                    Task(description=step.description),
                    to=step.delegate_to
                )
            else:
                results[step.id] = await self._execute_step(step)

        return await self._synthesize_results(results)
```

## Testing Agents

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock

class TestDataAnalystAgent:
    @pytest.fixture
    def mock_provider(self):
        provider = AsyncMock()
        provider.complete.return_value = CompletionResponse(
            content="Analysis complete",
            usage=TokenUsage(100, 50, 150)
        )
        return provider

    @pytest.fixture
    def agent(self, mock_provider):
        return DataAnalystAgent(
            provider=mock_provider,
            config=AgentConfig(max_iterations=3)
        )

    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        task = Task(id="test-1", description="Analyze sales data")
        result = await agent.execute(task)

        assert result.success
        assert result.output is not None
```

### Integration Testing

```python
@pytest.mark.integration
class TestAgentIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        # Use real provider with test API key
        provider = LLMProvider.create("anthropic", test_config)
        memory = MemoryStore(backend="in_memory")

        agent = DataAnalystAgent(
            provider=provider,
            config=AgentConfig(),
            memory=memory
        )

        result = await agent.execute(Task(
            id="int-test-1",
            description="Analyze the test dataset"
        ))

        assert result.success
        # Verify memory was updated
        memories = await memory.search_semantic("test dataset")
        assert len(memories) > 0
```

## Best Practices

1. **Single Responsibility** - Each agent should have a focused purpose
2. **Composability** - Design agents to work together
3. **Idempotency** - Tasks should be safely retryable
4. **Observability** - Log important decisions and actions
5. **Graceful Degradation** - Handle failures gracefully
6. **Resource Limits** - Set appropriate timeouts and limits

## See Also

- [Agent API Reference](../api/agent-api.md)
- [Skills Development](skill-development.md)
- [Tool Development](tool-development.md)
- [Workflow Development](workflow-development.md)
