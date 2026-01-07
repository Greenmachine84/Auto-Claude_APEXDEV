# Agent API Reference

Complete API documentation for the Auto-Claude agent system.

## Overview

The Agent API provides interfaces for creating, configuring, and orchestrating
autonomous agents that can perform complex tasks using LLM providers.

## Agent Types

### BaseAgent

Abstract base class for all agents.

```python
from apps.backend.agents import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, task: Task) -> TaskResult:
        # Implementation
        pass
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `execute` | `task: Task` | `TaskResult` | Execute a task |
| `plan` | `goal: str` | `list[Step]` | Create execution plan |
| `validate` | `result: Any` | `bool` | Validate task result |
| `rollback` | `task_id: str` | `bool` | Rollback failed task |

### CoderAgent

Specialized agent for code generation and modification.

```python
from apps.backend.agents import CoderAgent

agent = CoderAgent(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    capabilities=["python", "typescript", "review"]
)

result = await agent.write_code(
    specification="Create a REST API endpoint",
    language="python",
    framework="fastapi"
)
```

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | `str` | Required | LLM provider name |
| `model` | `str` | Required | Model identifier |
| `capabilities` | `list[str]` | `[]` | Enabled capabilities |
| `max_tokens` | `int` | `4096` | Max output tokens |
| `temperature` | `float` | `0.7` | Sampling temperature |

### ReviewerAgent

Agent for code review and quality analysis.

```python
from apps.backend.agents import ReviewerAgent

agent = ReviewerAgent(
    provider="openai",
    model="gpt-4o",
    review_rules=["security", "performance", "style"]
)

review = await agent.review_code(
    code=source_code,
    context={"language": "python", "framework": "django"}
)
```

#### Review Output

```python
@dataclass
class ReviewResult:
    approved: bool
    findings: list[Finding]
    suggestions: list[Suggestion]
    security_issues: list[SecurityIssue]
    score: float  # 0.0 to 1.0
```

## Agent Orchestration

### AgentOrchestrator

Manages multiple agents and coordinates task execution.

```python
from apps.backend.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Register agents
orchestrator.register("coder", coder_agent)
orchestrator.register("reviewer", reviewer_agent)

# Define workflow
workflow = orchestrator.create_workflow([
    Step(agent="coder", action="write_code"),
    Step(agent="reviewer", action="review"),
    Step(agent="coder", action="apply_fixes", condition="review.has_issues"),
])

# Execute
result = await orchestrator.execute(workflow, task)
```

### Workflow Configuration

```yaml
workflow:
  name: "code-generation"
  steps:
    - agent: coder
      action: write_code
      timeout: 300
    - agent: reviewer
      action: review
      retry: 3
    - agent: coder
      action: apply_fixes
      condition: "review.findings.length > 0"
```

## Agent Communication

### Message Protocol

```python
@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: Any
    message_type: MessageType
    correlation_id: str
    timestamp: datetime
```

### Event System

```python
# Subscribe to agent events
@orchestrator.on("task.completed")
async def on_task_complete(event: TaskEvent):
    logger.info(f"Task {event.task_id} completed")

@orchestrator.on("agent.error")
async def on_error(event: ErrorEvent):
    await handle_error(event)
```

## Error Handling

### Exception Types

| Exception | Description | Recovery |
|-----------|-------------|----------|
| `AgentError` | Base agent exception | Retry or escalate |
| `TaskTimeout` | Task execution timeout | Increase timeout |
| `ValidationError` | Invalid task input | Fix input |
| `ProviderError` | LLM provider failure | Fallback provider |

### Retry Configuration

```python
agent = CoderAgent(
    provider="anthropic",
    retry_config=RetryConfig(
        max_attempts=3,
        backoff_factor=2.0,
        retry_on=[RateLimitError, TimeoutError]
    )
)
```

## Best Practices

1. **Use appropriate agent types** - Match agent to task requirements
2. **Configure timeouts** - Set realistic execution limits
3. **Handle errors gracefully** - Implement retry and fallback logic
4. **Monitor agent performance** - Track metrics and logs
5. **Validate outputs** - Always verify agent results

## See Also

- [Memory API](memory-api.md)
- [LLM Provider API](llm-api.md)
- [Tool API](tool-api.md)
- [Getting Started Guide](../guides/getting-started.md)
