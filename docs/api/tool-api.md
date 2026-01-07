# Tool API Reference

Complete API documentation for the Auto-Claude tool system.

## Overview

The Tool API provides interfaces for defining, registering, and executing
tools that agents can use to interact with external systems.

## Core Concepts

### Tool Definition

Tools are defined with a schema describing their inputs and outputs.

```python
from apps.backend.tools import Tool, ToolSchema

@Tool(
    name="read_file",
    description="Read contents of a file",
    schema=ToolSchema(
        parameters={
            "path": {"type": "string", "description": "File path"},
            "encoding": {"type": "string", "default": "utf-8"}
        },
        required=["path"]
    )
)
async def read_file(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()
```

## Tool Registry

### Registering Tools

```python
from apps.backend.tools import ToolRegistry

registry = ToolRegistry()

# Register individual tool
registry.register(read_file)

# Register multiple tools
registry.register_all([
    read_file,
    write_file,
    search_code,
    run_command
])

# Register from module
registry.register_module(file_tools)
```

### Retrieving Tools

```python
# Get by name
tool = registry.get("read_file")

# Get by category
file_tools = registry.get_by_category("filesystem")

# List all
all_tools = registry.list_all()
```

## Tool Execution

### ToolExecutor

Executes tools with permission checking and sandboxing.

```python
from apps.backend.tools import ToolExecutor, ExecutionContext

executor = ToolExecutor(
    registry=registry,
    sandbox_mode=True,
    timeout=30
)

# Execute a tool
result = await executor.execute(
    tool_name="read_file",
    parameters={"path": "/path/to/file.txt"},
    context=ExecutionContext(
        user_id="user-123",
        permissions=["filesystem.read"]
    )
)
```

### Execution Result

```python
@dataclass
class ToolResult:
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: dict = field(default_factory=dict)
```

## Built-in Tools

### File System Tools

| Tool | Description | Permissions |
|------|-------------|-------------|
| `read_file` | Read file contents | `filesystem.read` |
| `write_file` | Write to file | `filesystem.write` |
| `list_directory` | List directory contents | `filesystem.read` |
| `create_directory` | Create directory | `filesystem.write` |
| `delete_file` | Delete file | `filesystem.delete` |
| `move_file` | Move/rename file | `filesystem.write` |

### Code Tools

| Tool | Description | Permissions |
|------|-------------|-------------|
| `search_code` | Search codebase | `code.read` |
| `analyze_code` | Analyze code structure | `code.read` |
| `format_code` | Format source code | `code.write` |
| `lint_code` | Run linter | `code.read` |

### Shell Tools

| Tool | Description | Permissions |
|------|-------------|-------------|
| `run_command` | Execute shell command | `shell.execute` |
| `run_script` | Execute script file | `shell.execute` |

### Network Tools

| Tool | Description | Permissions |
|------|-------------|-------------|
| `http_request` | Make HTTP request | `network.http` |
| `fetch_webpage` | Fetch web content | `network.http` |

## Custom Tool Definition

### Simple Tool

```python
from apps.backend.tools import Tool

@Tool(name="calculate", description="Perform calculation")
async def calculate(expression: str) -> float:
    # Safe evaluation
    return eval_safe(expression)
```

### Tool with Validation

```python
from apps.backend.tools import Tool, validate_input

@Tool(
    name="send_email",
    description="Send an email"
)
@validate_input({
    "to": {"type": "string", "format": "email"},
    "subject": {"type": "string", "max_length": 200},
    "body": {"type": "string"}
})
async def send_email(to: str, subject: str, body: str) -> bool:
    # Implementation
    pass
```

### Sandboxed Tool

```python
from apps.backend.tools import SandboxedTool

@SandboxedTool(
    name="run_code",
    description="Execute code in sandbox",
    allowed_paths=["/workspace"],
    blocked_modules=["os", "subprocess"],
    timeout=10
)
async def run_code(code: str, language: str) -> str:
    # Executed in restricted environment
    pass
```

## Permission System

### Permission Levels

| Level | Description |
|-------|-------------|
| `READ` | Read-only access |
| `WRITE` | Modify access |
| `EXECUTE` | Execution access |
| `ADMIN` | Full access |

### Checking Permissions

```python
from apps.backend.tools import check_permission

@check_permission("filesystem.write")
async def write_file(path: str, content: str):
    pass
```

### Permission Groups

```python
permissions = PermissionGroup([
    "filesystem.read",
    "filesystem.write",
    "code.read",
    "code.write"
])

executor = ToolExecutor(
    registry=registry,
    permissions=permissions
)
```

## Sandboxing

### Path Restrictions

```python
sandbox = SandboxConfig(
    allowed_paths=[
        "/workspace",
        "/tmp/tool-output"
    ],
    blocked_paths=[
        "/etc",
        "/var",
        "~/.ssh"
    ]
)
```

### Resource Limits

```python
sandbox = SandboxConfig(
    max_memory_mb=512,
    max_cpu_seconds=30,
    max_file_size_mb=10,
    max_open_files=100
)
```

## Batch Execution

Execute multiple tools in parallel.

```python
results = await executor.execute_batch([
    ToolCall("read_file", {"path": "file1.txt"}),
    ToolCall("read_file", {"path": "file2.txt"}),
    ToolCall("search_code", {"query": "TODO"})
])

for result in results:
    if result.success:
        print(result.output)
```

## Tool Chaining

Chain tools together for complex operations.

```python
from apps.backend.tools import ToolChain

chain = ToolChain([
    ("read_file", {"path": "input.txt"}),
    ("analyze_code", {"source": "$previous.output"}),
    ("write_file", {"path": "analysis.json", "content": "$previous.output"})
])

final_result = await executor.execute_chain(chain)
```

## Error Handling

### Exception Types

| Exception | Description |
|-----------|-------------|
| `ToolError` | Base tool exception |
| `ToolNotFoundError` | Tool not registered |
| `PermissionDeniedError` | Insufficient permissions |
| `ValidationError` | Invalid parameters |
| `SandboxViolation` | Sandbox restriction violated |
| `TimeoutError` | Execution timeout |

### Error Handling Example

```python
from apps.backend.tools.exceptions import (
    PermissionDeniedError,
    SandboxViolation
)

try:
    result = await executor.execute("write_file", params)
except PermissionDeniedError:
    logger.warning("Permission denied for file write")
except SandboxViolation as e:
    logger.error(f"Sandbox violation: {e.violation_type}")
```

## Monitoring

### Execution Metrics

```python
metrics = executor.get_metrics()
print(f"Total executions: {metrics.total}")
print(f"Success rate: {metrics.success_rate:.1%}")
print(f"Avg duration: {metrics.avg_duration_ms}ms")
```

### Audit Logging

```python
executor = ToolExecutor(
    registry=registry,
    audit_log=AuditLogger(
        destination="file",
        path="/var/log/tool-audit.log"
    )
)
```

## Best Practices

1. **Define clear schemas** - Document all parameters
2. **Validate inputs** - Prevent injection attacks
3. **Use sandboxing** - Limit tool capabilities
4. **Set timeouts** - Prevent hanging executions
5. **Log all executions** - Enable auditing
6. **Handle errors gracefully** - Provide useful feedback

## See Also

- [Agent API](agent-api.md)
- [Tool Development Guide](../guides/tool-development.md)
- [Security Overview](../security/security-overview.md)
