# Tool Development Guide

A comprehensive guide to developing custom tools for Auto-Claude agents.

## Overview

Tools extend agent capabilities by providing interfaces to external systems,
file operations, code execution, and other functionality.

## Tool Architecture

```
┌─────────────────────────────────────────┐
│              Tool Registry              │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  File   │  │  Code   │  │  Shell  │ │
│  │  Tools  │  │  Tools  │  │  Tools  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
├─────────────────────────────────────────┤
│              Tool Executor              │
│  (Permission Check → Sandbox → Execute) │
└─────────────────────────────────────────┘
```

## Creating a Basic Tool

### Using the Decorator

```python
from apps.backend.tools import Tool, ToolSchema

@Tool(
    name="word_count",
    description="Count words in text",
    schema=ToolSchema(
        parameters={
            "text": {"type": "string", "description": "Text to count"}
        },
        required=["text"]
    )
)
async def word_count(text: str) -> dict:
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text)
    }
```

### Using a Class

```python
from apps.backend.tools import BaseTool, ToolResult

class WordCountTool(BaseTool):
    name = "word_count"
    description = "Count words in text"

    schema = ToolSchema(
        parameters={
            "text": {"type": "string", "description": "Text to count"}
        },
        required=["text"]
    )

    async def execute(self, text: str) -> ToolResult:
        words = text.split()
        return ToolResult(
            success=True,
            output={"word_count": len(words), "char_count": len(text)}
        )
```

## Tool Schema

### Parameter Types

```python
schema = ToolSchema(
    parameters={
        "text": {
            "type": "string",
            "description": "Input text",
            "min_length": 1,
            "max_length": 10000
        },
        "count": {
            "type": "integer",
            "description": "Number of items",
            "min": 1,
            "max": 100,
            "default": 10
        },
        "enabled": {
            "type": "boolean",
            "description": "Enable feature",
            "default": True
        },
        "options": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of options"
        },
        "config": {
            "type": "object",
            "properties": {
                "key": {"type": "string"}
            }
        }
    },
    required=["text"]
)
```

### Enum Parameters

```python
schema = ToolSchema(
    parameters={
        "format": {
            "type": "string",
            "enum": ["json", "yaml", "xml"],
            "description": "Output format"
        }
    }
)
```

## File System Tools

### Reading Files

```python
@Tool(
    name="read_file",
    description="Read file contents",
    category="filesystem",
    permissions=["filesystem.read"]
)
async def read_file(
    path: str,
    encoding: str = "utf-8",
    start_line: int = None,
    end_line: int = None
) -> str:
    # Validate path
    safe_path = sanitize_path(path)

    with open(safe_path, "r", encoding=encoding) as f:
        lines = f.readlines()

    if start_line or end_line:
        start = (start_line or 1) - 1
        end = end_line or len(lines)
        lines = lines[start:end]

    return "".join(lines)
```

### Writing Files

```python
@Tool(
    name="write_file",
    description="Write content to file",
    category="filesystem",
    permissions=["filesystem.write"]
)
async def write_file(
    path: str,
    content: str,
    create_dirs: bool = True
) -> dict:
    safe_path = sanitize_path(path)

    if create_dirs:
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)

    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"path": safe_path, "bytes_written": len(content)}
```

## Code Analysis Tools

### Search Code

```python
@Tool(
    name="search_code",
    description="Search for patterns in code",
    category="code",
    permissions=["code.read"]
)
async def search_code(
    pattern: str,
    path: str = ".",
    file_types: list[str] = None,
    max_results: int = 100
) -> list[dict]:
    results = []
    regex = re.compile(pattern)

    for root, _, files in os.walk(path):
        for file in files:
            if file_types and not any(file.endswith(ft) for ft in file_types):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r") as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append({
                                "file": file_path,
                                "line": i,
                                "content": line.strip()
                            })
                            if len(results) >= max_results:
                                return results
            except (IOError, UnicodeDecodeError):
                continue

    return results
```

## Shell Tools

### Execute Command

```python
@Tool(
    name="run_command",
    description="Execute shell command",
    category="shell",
    permissions=["shell.execute"],
    timeout=60
)
async def run_command(
    command: str,
    cwd: str = None,
    env: dict = None
) -> dict:
    # Validate command
    if not is_safe_command(command):
        raise SecurityError("Command contains unsafe patterns")

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env={**os.environ, **(env or {})}
    )

    stdout, stderr = await process.communicate()

    return {
        "exit_code": process.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode()
    }
```

## Network Tools

### HTTP Request

```python
@Tool(
    name="http_request",
    description="Make HTTP request",
    category="network",
    permissions=["network.http"]
)
async def http_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    body: str = None,
    timeout: int = 30
) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method,
            url,
            headers=headers,
            data=body,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": await response.text()
            }
```

## Permission System

### Defining Permissions

```python
@Tool(
    name="sensitive_operation",
    permissions=["admin.write", "data.modify"]
)
async def sensitive_operation(data: str) -> dict:
    # Tool requires both permissions
    pass
```

### Permission Levels

| Permission | Description |
|------------|-------------|
| `filesystem.read` | Read files |
| `filesystem.write` | Write files |
| `filesystem.delete` | Delete files |
| `code.read` | Read/analyze code |
| `code.write` | Modify code |
| `shell.execute` | Run shell commands |
| `network.http` | Make HTTP requests |
| `admin.*` | Administrative operations |

## Sandboxing

### Path Restrictions

```python
@Tool(
    name="safe_read",
    sandbox=SandboxConfig(
        allowed_paths=["/workspace", "/tmp"],
        blocked_paths=["/etc", "/var", "~/.ssh"]
    )
)
async def safe_read(path: str) -> str:
    # Path is automatically validated
    return await read_file_impl(path)
```

### Resource Limits

```python
@Tool(
    name="resource_limited",
    sandbox=SandboxConfig(
        max_memory_mb=256,
        max_cpu_seconds=10,
        max_output_size=1024 * 1024  # 1MB
    )
)
async def resource_limited(data: str) -> str:
    pass
```

## Error Handling

### Tool Exceptions

```python
from apps.backend.tools.exceptions import (
    ToolError,
    ValidationError,
    PermissionDeniedError,
    TimeoutError
)

@Tool(name="validated_tool")
async def validated_tool(value: int) -> int:
    if value < 0:
        raise ValidationError("Value must be non-negative")
    if value > 1000:
        raise ToolError("Value too large to process")
    return value * 2
```

### Error Recovery

```python
@Tool(
    name="resilient_tool",
    retry_config=RetryConfig(
        max_attempts=3,
        backoff_factor=2.0,
        retry_on=[TimeoutError, ConnectionError]
    )
)
async def resilient_tool(url: str) -> dict:
    return await fetch_data(url)
```

## Testing Tools

### Unit Tests

```python
import pytest
from apps.backend.tools import ToolExecutor

class TestWordCountTool:
    @pytest.fixture
    def executor(self):
        registry = ToolRegistry()
        registry.register(word_count)
        return ToolExecutor(registry=registry)

    @pytest.mark.asyncio
    async def test_count_words(self, executor):
        result = await executor.execute(
            "word_count",
            {"text": "hello world test"}
        )
        assert result.success
        assert result.output["word_count"] == 3

    @pytest.mark.asyncio
    async def test_empty_text(self, executor):
        result = await executor.execute(
            "word_count",
            {"text": ""}
        )
        assert result.success
        assert result.output["word_count"] == 0
```

### Integration Tests

```python
@pytest.mark.integration
class TestFileTools:
    @pytest.mark.asyncio
    async def test_read_write_cycle(self, tmp_path):
        executor = ToolExecutor(registry=file_tools_registry)

        # Write
        write_result = await executor.execute(
            "write_file",
            {"path": str(tmp_path / "test.txt"), "content": "hello"}
        )
        assert write_result.success

        # Read
        read_result = await executor.execute(
            "read_file",
            {"path": str(tmp_path / "test.txt")}
        )
        assert read_result.output == "hello"
```

## Best Practices

1. **Validate all inputs** - Never trust user input
2. **Use appropriate permissions** - Principle of least privilege
3. **Set timeouts** - Prevent hanging operations
4. **Handle errors gracefully** - Provide useful error messages
5. **Document thoroughly** - Clear descriptions and examples
6. **Test extensively** - Unit and integration tests

## See Also

- [Tool API Reference](../api/tool-api.md)
- [Security Overview](../security/security-overview.md)
- [Agent Development](agent-development.md)
