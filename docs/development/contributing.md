# Contributing Guide

Guidelines for contributing to Auto-Claude.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional)

### Development Setup

```bash
# Clone repository
git clone https://github.com/Greenmachine84/Auto-Claude_APEXDEV.git
cd Auto-Claude_APEXDEV

# Install backend dependencies
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Install frontend dependencies
cd ../frontend
pnpm install
```

### Running Tests

```bash
# Backend tests
cd apps/backend
pytest tests/ -v

# Frontend tests
cd apps/frontend
pnpm test
```

## Development Workflow

### Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation |

### Commit Messages

Follow [Conventional Commits](https://conventionalcommits.org):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

**Examples**:
```
feat(agents): add multi-agent orchestration
fix(memory): resolve embedding cache issue
docs(api): update tool API reference
```

### Pull Requests

1. **Create feature branch** from `develop`
2. **Make changes** with tests
3. **Run linting** - `ruff check .`
4. **Run tests** - `pytest`
5. **Submit PR** with description
6. **Address review** feedback
7. **Merge** after approval

### PR Template

```markdown
## Description
[What does this PR do?]

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes
```

## Code Standards

### Python

- **Style**: PEP 8, enforced by Ruff
- **Type hints**: Required for all functions
- **Docstrings**: Google style
- **Max line length**: 100 characters

```python
def process_task(
    task: str,
    *,
    timeout: int = 30,
    retry: bool = True,
) -> TaskResult:
    """Process a task with the agent.
    
    Args:
        task: The task description.
        timeout: Timeout in seconds.
        retry: Whether to retry on failure.
        
    Returns:
        The task execution result.
        
    Raises:
        TaskError: If processing fails.
    """
    pass
```

### TypeScript

- **Style**: ESLint + Prettier
- **Types**: Explicit types, avoid `any`
- **Imports**: Organized by category

```typescript
// External imports
import { useState, useEffect } from 'react';

// Internal imports
import { AgentClient } from '@/services/agent';
import type { Task } from '@/types';

// Component
export function TaskView({ taskId }: TaskViewProps): JSX.Element {
  // Implementation
}
```

### Testing Standards

- **Coverage**: Minimum 80%
- **Naming**: `test_<function>_<scenario>`
- **Fixtures**: Use pytest fixtures
- **Mocking**: Mock external services

```python
def test_agent_execute_success():
    """Test successful agent execution."""
    agent = CoderAgent()
    result = agent.execute("Create hello world")
    assert result.status == "success"

def test_agent_execute_handles_timeout():
    """Test agent handles timeout gracefully."""
    with pytest.raises(TimeoutError):
        agent.execute("Long task", timeout=0.1)
```

## Documentation

### Requirements

- API changes must update docs
- New features need guides
- Complex code needs comments

### Style

- Use present tense
- Be concise
- Include examples
- Link related docs

## Review Process

### Review Criteria

- [ ] Code quality and style
- [ ] Test coverage
- [ ] Documentation
- [ ] Performance impact
- [ ] Security considerations

### Reviewers

- 1 approval required for bug fixes
- 2 approvals for features
- Architecture review for major changes

## Community

### Communication

- GitHub Issues for bugs
- Discussions for questions
- Discord for real-time chat

### Code of Conduct

- Be respectful
- Be constructive
- Be inclusive

## See Also

- [Testing Guide](testing.md)
- [Architecture](architecture.md)
- [Code Style](code-style.md)
