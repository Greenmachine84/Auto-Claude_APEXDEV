# Getting Started with Auto-Claude

A comprehensive guide to setting up and running your first Auto-Claude agent.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** for the frontend
- **Git** for version control
- An API key for at least one LLM provider

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/Auto-Claude.git
cd Auto-Claude
```

### 2. Install Backend Dependencies

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd apps/frontend
pnpm install
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# Required: At least one LLM provider
ANTHROPIC_API_KEY=your-anthropic-key
# Or
OPENAI_API_KEY=your-openai-key

# Optional: Additional providers
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
GOOGLE_API_KEY=your-google-key
OPENROUTER_API_KEY=your-openrouter-key

# Memory storage (optional)
MEMORY_BACKEND=in_memory  # or "chromadb", "file"

# Logging
LOG_LEVEL=INFO
```

## Quick Start

### Running Your First Agent

```python
import asyncio
from apps.backend.agents import CoderAgent
from apps.backend.llm import LLMProvider, ProviderConfig

async def main():
    # Create an LLM provider
    provider = LLMProvider.create(
        provider_type="anthropic",
        config=ProviderConfig(
            api_key="your-api-key",
            model="claude-sonnet-4-20250514"
        )
    )

    # Create an agent
    agent = CoderAgent(
        provider=provider,
        capabilities=["python", "review"]
    )

    # Execute a task
    result = await agent.execute_task(
        "Create a Python function that calculates fibonacci numbers"
    )

    print(result.output)

asyncio.run(main())
```

### Using the CLI

```bash
# Start the backend server
python -m apps.backend.main

# In another terminal, run an agent task
python run.py/agent.py --task "Review this code for issues" --file example.py
```

### Starting the Frontend

```bash
cd apps/frontend
pnpm dev
```

Open http://localhost:3000 in your browser.

## Core Concepts

### Agents

Agents are autonomous entities that perform tasks using LLM capabilities.

| Agent Type | Purpose |
|------------|---------|
| `CoderAgent` | Code generation and modification |
| `ReviewerAgent` | Code review and quality analysis |
| `PlannerAgent` | Task planning and decomposition |
| `ResearcherAgent` | Information gathering |

### Memory

Memory stores information across agent sessions:

- **Episodic**: Event-based memories
- **Semantic**: Factual knowledge
- **Procedural**: How-to knowledge
- **Working**: Active context

### Tools

Tools extend agent capabilities:

- File system operations
- Code search and analysis
- Shell command execution
- HTTP requests

### Workflows

Workflows orchestrate multiple agents:

```python
workflow = Workflow(
    steps=[
        Step(agent="planner", action="plan"),
        Step(agent="coder", action="implement"),
        Step(agent="reviewer", action="review")
    ]
)
```

## Project Structure

```
Auto-Claude/
├── apps/
│   ├── backend/           # Python backend
│   │   ├── agents/        # Agent implementations
│   │   ├── llm/           # LLM providers
│   │   ├── memory/        # Memory system
│   │   ├── tools/         # Tool definitions
│   │   └── orchestrator/  # Workflow orchestration
│   └── frontend/          # Electron/React frontend
├── docs/                  # Documentation
├── tests/                 # Test suite
└── scripts/               # Utility scripts
```

## Configuration

### LLM Providers

Configure your preferred LLM provider:

```python
# Anthropic (recommended)
provider = LLMProvider.create("anthropic", config)

# OpenAI
provider = LLMProvider.create("openai", config)

# Local (Ollama)
provider = LLMProvider.create("ollama", ProviderConfig(
    base_url="http://localhost:11434",
    model="llama3.2"
))
```

### Memory Backend

Choose your memory storage:

```python
# In-memory (development)
store = MemoryStore(backend="in_memory")

# File-based
store = MemoryStore(
    backend="file",
    config={"path": "./data/memory"}
)

# Vector database (production)
store = MemoryStore(
    backend="chromadb",
    config={"persist_directory": "./data/chroma"}
)
```

## Example: Code Review Workflow

```python
import asyncio
from apps.backend.agents import CoderAgent, ReviewerAgent
from apps.backend.orchestrator import Orchestrator, Workflow, WorkflowStep

async def code_review_workflow():
    # Initialize orchestrator
    orchestrator = Orchestrator()

    # Register agents
    orchestrator.register("coder", CoderAgent(provider=anthropic))
    orchestrator.register("reviewer", ReviewerAgent(provider=openai))

    # Define workflow
    workflow = Workflow(
        id="review-flow",
        steps=[
            WorkflowStep(
                id="write",
                agent="coder",
                action="write_code",
                inputs={"spec": "$workflow.input.specification"}
            ),
            WorkflowStep(
                id="review",
                agent="reviewer",
                action="review_code",
                inputs={"code": "$steps.write.output.code"},
                depends_on=["write"]
            ),
            WorkflowStep(
                id="fix",
                agent="coder",
                action="apply_fixes",
                inputs={
                    "code": "$steps.write.output.code",
                    "review": "$steps.review.output"
                },
                condition="$steps.review.output.has_issues",
                depends_on=["review"]
            )
        ]
    )

    # Execute
    result = await orchestrator.execute(
        workflow,
        input={"specification": "Create a REST API endpoint for user login"}
    )

    return result

asyncio.run(code_review_workflow())
```

## Troubleshooting

### Common Issues

#### API Key Not Found

```
Error: ANTHROPIC_API_KEY not set
```

**Solution**: Ensure your `.env` file exists and contains valid API keys.

#### Model Not Available

```
Error: Model claude-sonnet-4-20250514 not found
```

**Solution**: Verify the model name and your API key's access level.

#### Memory Persistence Failed

```
Error: Failed to persist memory
```

**Solution**: Check write permissions to the storage directory.

### Getting Help

- Check the [API Reference](../api/index.md)
- Review [Troubleshooting Guide](troubleshooting.md)
- Open an issue on GitHub

## Next Steps

- [Agent Development Guide](agent-development.md) - Build custom agents
- [Memory Management](memory-management.md) - Configure memory systems
- [Tool Development](tool-development.md) - Create custom tools
- [Deployment Guide](deployment.md) - Deploy to production
