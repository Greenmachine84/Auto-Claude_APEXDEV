# API Reference Index

Complete API documentation for Auto-Claude.

## Overview

This section provides comprehensive API reference documentation for all
Auto-Claude components and subsystems.

## Core APIs

### Agent System

- [Agent API](agent-api.md) - Agent creation, configuration, and orchestration
- [Orchestrator API](orchestrator-api.md) - Workflow coordination and task management
- [Skills API](skills-api.md) - Reusable agent capabilities

### Infrastructure

- [Memory API](memory-api.md) - Memory storage, retrieval, and semantic search
- [LLM Provider API](llm-api.md) - Language model provider integration
- [Tool API](tool-api.md) - Tool definition and execution

### Security

- [Security API](security-api.md) - Authentication, authorization, and scanning

## Quick Reference

### Creating an Agent

```python
from apps.backend.agents import CoderAgent, AgentConfig

agent = CoderAgent(
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    config=AgentConfig(
        max_tokens=4096,
        temperature=0.7
    )
)

result = await agent.execute(task)
```

### Storing Memory

```python
from apps.backend.memory import MemoryStore, MemoryEntry

store = MemoryStore(backend="vector_db")

await store.store(MemoryEntry(
    id="mem-1",
    content="Important information",
    category=MemoryCategory.SEMANTIC
))
```

### Using Tools

```python
from apps.backend.tools import ToolRegistry, ToolExecutor

registry = ToolRegistry()
registry.register(read_file)

executor = ToolExecutor(registry=registry)
result = await executor.execute("read_file", {"path": "file.txt"})
```

### LLM Completion

```python
from apps.backend.llm import LLMProvider

provider = LLMProvider.create("anthropic", config)
response = await provider.complete(messages)
```

## Common Patterns

### Error Handling

All APIs use consistent exception handling:

```python
try:
    result = await api.operation()
except ValidationError as e:
    # Handle invalid input
except NotFoundError as e:
    # Handle missing resource
except AuthorizationError as e:
    # Handle permission denied
except APIError as e:
    # Handle other errors
```

### Async Operations

All I/O operations are async:

```python
# Sequential
result1 = await operation1()
result2 = await operation2()

# Parallel
results = await asyncio.gather(
    operation1(),
    operation2()
)
```

### Configuration

APIs accept configuration objects:

```python
config = APIConfig(
    timeout=30,
    retry_attempts=3,
    logging_level="INFO"
)

api = API(config=config)
```

## Version Compatibility

| API Version | Python Version | Status |
|-------------|----------------|--------|
| 1.0.x | 3.10+ | Current |

## See Also

- [Getting Started Guide](../guides/getting-started.md)
- [Architecture Overview](../architecture/README.md)
- [Examples](../examples/README.md)
