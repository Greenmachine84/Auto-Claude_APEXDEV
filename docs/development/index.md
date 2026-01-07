# Development Documentation Index

Developer documentation for Auto-Claude.

## Quick Start

1. [Contributing Guide](contributing.md) - Setup and workflow
2. [Testing Guide](testing.md) - Writing and running tests

## Documentation Overview

| Document | Description |
|----------|-------------|
| [Contributing](contributing.md) | Development setup, workflow, standards |
| [Testing](testing.md) | Test structure, writing tests, coverage |

## Development Commands

```bash
# Setup
pnpm install           # Install dependencies
pip install -e ".[dev]" # Install Python with dev extras

# Testing
pytest                 # Run all tests
pytest -v --tb=short  # Verbose with short traceback
pytest --cov          # With coverage

# Linting
ruff check .          # Check Python
ruff format .         # Format Python
pnpm lint            # Check TypeScript

# Building
pnpm build           # Build frontend
```

## See Also

- [API Reference](../api/index.md)
- [User Guides](../guides/index.md)
- [Security Docs](../security/index.md)
