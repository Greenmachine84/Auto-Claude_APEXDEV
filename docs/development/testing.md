# Testing Guide

Comprehensive testing documentation for Auto-Claude.

## Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── e2e/              # End-to-end tests
├── fixtures/         # Test fixtures
├── mocks/            # Mock implementations
└── conftest.py       # Shared pytest config
```

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=apps/backend --cov-report=html

# Verbose output
pytest -v
```

### Specific Tests

```bash
# Single file
pytest tests/unit/test_agent.py

# Single test
pytest tests/unit/test_agent.py::test_execute_success

# By marker
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
```

### Test Options

```bash
# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables
pytest -l

# Re-run failed tests
pytest --lf
```

## Writing Tests

### Unit Tests

```python
# tests/unit/test_agent.py
import pytest
from apps.backend.agents import CoderAgent

class TestCoderAgent:
    """Unit tests for CoderAgent."""
    
    def test_init_default_config(self):
        """Test default configuration."""
        agent = CoderAgent()
        assert agent.role == "coder"
        assert agent.llm_provider is not None
    
    def test_execute_returns_result(self, mock_llm):
        """Test execute returns proper result."""
        agent = CoderAgent(llm_provider=mock_llm)
        result = agent.execute("Create function")
        assert result.status == "success"
        assert result.output is not None
    
    def test_execute_handles_empty_task(self):
        """Test empty task raises error."""
        agent = CoderAgent()
        with pytest.raises(ValueError, match="Task cannot be empty"):
            agent.execute("")
```

### Integration Tests

```python
# tests/integration/test_agent_memory.py
import pytest
from apps.backend.agents import CoderAgent
from apps.backend.memory import MemoryStore

@pytest.mark.integration
class TestAgentMemoryIntegration:
    """Integration tests for agent-memory interaction."""
    
    @pytest.fixture
    def agent_with_memory(self, temp_db):
        """Create agent with real memory store."""
        memory = MemoryStore(database=temp_db)
        return CoderAgent(memory=memory)
    
    def test_agent_stores_context(self, agent_with_memory):
        """Test agent stores context to memory."""
        agent_with_memory.execute("Create user model")
        
        results = agent_with_memory.memory.search("user model")
        assert len(results) > 0
```

### End-to-End Tests

```python
# tests/e2e/test_full_workflow.py
import pytest

@pytest.mark.e2e
@pytest.mark.slow
class TestFullWorkflow:
    """End-to-end workflow tests."""
    
    def test_complete_coding_task(self, running_server, test_project):
        """Test complete coding workflow."""
        client = APIClient(running_server)
        
        # Create task
        task = client.create_task("Add login feature")
        assert task.id is not None
        
        # Execute
        result = client.execute_task(task.id)
        assert result.status == "completed"
        
        # Verify files created
        assert test_project.has_file("auth/login.py")
```

## Fixtures

### Common Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for tests."""
    return tmp_path

@pytest.fixture
def sample_project(temp_dir):
    """Sample project structure."""
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("# main")
    return temp_dir

@pytest.fixture
def mock_llm():
    """Mock LLM provider."""
    from tests.mocks.llm_mock import MockLLMProvider
    return MockLLMProvider()

@pytest.fixture
def mock_memory():
    """Mock memory store."""
    from tests.mocks.memory_mock import MockMemoryStore
    return MockMemoryStore()
```

### Database Fixtures

```python
@pytest.fixture
async def temp_db(temp_dir):
    """Temporary database for tests."""
    db_path = temp_dir / "test.db"
    db = await Database.create(db_path)
    yield db
    await db.close()

@pytest.fixture
async def populated_db(temp_db):
    """Database with sample data."""
    await temp_db.execute("INSERT INTO users ...")
    return temp_db
```

## Mocking

### Mock LLM Provider

```python
# tests/mocks/llm_mock.py
class MockLLMProvider:
    """Mock LLM for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []
    
    async def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.get(prompt, "Mock response")
    
    async def stream(self, prompt: str):
        response = await self.complete(prompt)
        for char in response:
            yield char
```

### Patching

```python
from unittest.mock import patch, MagicMock

def test_external_api_call():
    """Test with patched external call."""
    with patch("apps.backend.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        
        result = fetch_status()
        
        assert result == "ok"
        mock_get.assert_called_once()
```

## Test Markers

### Available Markers

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    requires_api: Tests requiring API access
```

### Using Markers

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_integration_slow():
    pass

@pytest.mark.skip(reason="Not implemented")
def test_future_feature():
    pass

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix only"
)
def test_unix_specific():
    pass
```

## Coverage

### Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["apps/backend"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Reports

```bash
# HTML report
pytest --cov=apps/backend --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=apps/backend --cov-report=xml
```

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
```

## Best Practices

### Do's

- Test one thing per test
- Use descriptive test names
- Use fixtures for setup
- Test edge cases
- Test error handling

### Don'ts

- Don't test implementation details
- Don't use sleep for timing
- Don't depend on test order
- Don't share state between tests

## See Also

- [Contributing Guide](contributing.md)
- [Architecture](architecture.md)
- [API Reference](../api/index.md)
