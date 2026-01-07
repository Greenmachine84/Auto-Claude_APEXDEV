# Orchestrator API Reference

Complete API documentation for the Auto-Claude orchestration system.

## Overview

The Orchestrator API provides interfaces for coordinating complex multi-agent
workflows, managing task queues, and handling distributed execution.

## Core Components

### Orchestrator

Central coordinator for agent workflows.

```python
from apps.backend.orchestrator import Orchestrator, OrchestratorConfig

orchestrator = Orchestrator(
    config=OrchestratorConfig(
        max_concurrent_tasks=10,
        task_timeout=300,
        retry_policy=RetryPolicy.EXPONENTIAL
    )
)

await orchestrator.start()
```

#### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_concurrent_tasks` | `int` | `10` | Max parallel tasks |
| `task_timeout` | `int` | `300` | Default timeout (seconds) |
| `retry_policy` | `RetryPolicy` | `EXPONENTIAL` | Retry strategy |
| `queue_backend` | `str` | `memory` | Task queue backend |

## Workflow Definition

### Creating Workflows

```python
from apps.backend.orchestrator import Workflow, WorkflowStep

workflow = Workflow(
    id="code-review-workflow",
    name="Code Review Pipeline",
    steps=[
        WorkflowStep(
            id="analyze",
            agent="analyzer",
            action="analyze_changes",
            inputs={"diff": "$workflow.input.diff"}
        ),
        WorkflowStep(
            id="review",
            agent="reviewer",
            action="review_code",
            inputs={"analysis": "$steps.analyze.output"},
            depends_on=["analyze"]
        ),
        WorkflowStep(
            id="summarize",
            agent="summarizer",
            action="create_summary",
            inputs={
                "analysis": "$steps.analyze.output",
                "review": "$steps.review.output"
            },
            depends_on=["analyze", "review"]
        )
    ]
)
```

### Workflow Variables

| Variable Pattern | Description |
|-----------------|-------------|
| `$workflow.input.*` | Workflow input parameters |
| `$steps.<id>.output` | Output from a step |
| `$steps.<id>.status` | Status of a step |
| `$context.*` | Execution context values |

### Conditional Steps

```python
WorkflowStep(
    id="fix_issues",
    agent="coder",
    action="apply_fixes",
    condition="$steps.review.output.has_issues == true",
    depends_on=["review"]
)
```

## Task Management

### Task Submission

```python
task = Task(
    id="task-123",
    workflow_id="code-review-workflow",
    input={"diff": diff_content},
    priority=TaskPriority.HIGH,
    metadata={"pr_number": 42}
)

task_id = await orchestrator.submit(task)
```

### Task States

| State | Description |
|-------|-------------|
| `PENDING` | Waiting to be picked up |
| `RUNNING` | Currently executing |
| `COMPLETED` | Successfully finished |
| `FAILED` | Execution failed |
| `CANCELLED` | Manually cancelled |
| `TIMEOUT` | Exceeded time limit |

### Monitoring Tasks

```python
# Get task status
status = await orchestrator.get_status(task_id)
print(f"State: {status.state}")
print(f"Progress: {status.progress}%")

# Get task result
result = await orchestrator.get_result(task_id)
if result.success:
    print(result.output)
```

### Cancelling Tasks

```python
cancelled = await orchestrator.cancel(task_id)
```

## Agent Registration

### Registering Agents

```python
from apps.backend.agents import CoderAgent, ReviewerAgent

# Register individual agent
orchestrator.register_agent("coder", coder_agent)

# Register with capabilities
orchestrator.register_agent(
    "reviewer",
    reviewer_agent,
    capabilities=["python", "typescript", "security"]
)
```

### Agent Selection

```python
# Select by capability
agent = orchestrator.select_agent(
    role="coder",
    required_capabilities=["python", "async"]
)
```

## Parallel Execution

### Parallel Steps

```python
workflow = Workflow(
    steps=[
        WorkflowStep(id="step1", agent="a1", action="process"),
        WorkflowStep(id="step2", agent="a2", action="process"),
        WorkflowStep(id="step3", agent="a3", action="process"),
        WorkflowStep(
            id="merge",
            agent="merger",
            action="combine",
            depends_on=["step1", "step2", "step3"]
        )
    ]
)
```

### Fan-Out/Fan-In

```python
# Process items in parallel
workflow = Workflow(
    steps=[
        WorkflowStep(
            id="distribute",
            action="fan_out",
            fan_out_config=FanOutConfig(
                items_path="$workflow.input.files",
                max_parallel=5
            )
        ),
        WorkflowStep(
            id="process",
            agent="processor",
            action="process_item",
            inputs={"item": "$fan_out.current_item"}
        ),
        WorkflowStep(
            id="collect",
            action="fan_in",
            inputs={"results": "$steps.process.all_outputs"}
        )
    ]
)
```

## Error Handling

### Retry Configuration

```python
WorkflowStep(
    id="flaky_step",
    agent="agent",
    action="do_work",
    retry_config=RetryConfig(
        max_attempts=3,
        backoff_factor=2.0,
        retry_on=[TimeoutError, TemporaryError]
    )
)
```

### Fallback Steps

```python
WorkflowStep(
    id="primary",
    agent="primary_agent",
    action="process",
    fallback=WorkflowStep(
        id="fallback",
        agent="fallback_agent",
        action="process_simple"
    )
)
```

### Error Handlers

```python
@workflow.on_error("review")
async def handle_review_error(error: WorkflowError):
    if isinstance(error.cause, RateLimitError):
        await asyncio.sleep(60)
        return RetryAction()
    return FailAction(message=str(error))
```

## Events

### Subscribing to Events

```python
@orchestrator.on("task.started")
async def on_task_started(event: TaskEvent):
    logger.info(f"Task {event.task_id} started")

@orchestrator.on("task.completed")
async def on_task_completed(event: TaskEvent):
    await notify_completion(event.task_id)

@orchestrator.on("step.failed")
async def on_step_failed(event: StepEvent):
    await alert_on_failure(event)
```

### Event Types

| Event | Payload |
|-------|---------|
| `task.started` | `TaskEvent` |
| `task.completed` | `TaskEvent` with result |
| `task.failed` | `TaskEvent` with error |
| `step.started` | `StepEvent` |
| `step.completed` | `StepEvent` with output |
| `step.failed` | `StepEvent` with error |

## Persistence

### State Persistence

```python
orchestrator = Orchestrator(
    config=OrchestratorConfig(
        persistence_backend="redis",
        persistence_config={
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    )
)
```

### Workflow Recovery

```python
# Resume incomplete workflows after restart
await orchestrator.recover_workflows()
```

## Metrics

### Getting Metrics

```python
metrics = orchestrator.get_metrics()
print(f"Active tasks: {metrics.active_tasks}")
print(f"Completed: {metrics.completed_tasks}")
print(f"Failed: {metrics.failed_tasks}")
print(f"Avg duration: {metrics.avg_duration_ms}ms")
```

### Prometheus Export

```python
from apps.backend.orchestrator.metrics import PrometheusExporter

exporter = PrometheusExporter(orchestrator)
exporter.start(port=9090)
```

## Best Practices

1. **Design idempotent steps** - Enable safe retries
2. **Set appropriate timeouts** - Prevent stuck workflows
3. **Use dependency graphs** - Optimize parallel execution
4. **Monitor actively** - Track progress and failures
5. **Persist state** - Enable recovery after crashes
6. **Handle partial failures** - Define fallback strategies

## See Also

- [Agent API](agent-api.md)
- [Workflow Guide](../guides/workflow-development.md)
- [Deployment Guide](../guides/deployment.md)
