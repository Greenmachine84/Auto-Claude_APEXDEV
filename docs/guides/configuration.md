# Configuration Guide

Complete guide to configuring Auto-Claude.

## Environment Variables

### Required Variables

```bash
# At least one LLM provider API key is required
ANTHROPIC_API_KEY=your-anthropic-key
# OR
OPENAI_API_KEY=your-openai-key
```

### Optional LLM Providers

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Google
GOOGLE_API_KEY=your-google-key

# OpenRouter
OPENROUTER_API_KEY=your-openrouter-key

# Local (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### Memory Configuration

```bash
# Backend: in_memory, file, chromadb, postgres
MEMORY_BACKEND=chromadb

# ChromaDB settings
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=agent_memories

# PostgreSQL settings
DATABASE_URL=postgresql://user:pass@localhost/autoclaude
```

### Security Settings

```bash
# JWT configuration
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Sandbox settings
SANDBOX_ENABLED=true
SANDBOX_ALLOWED_PATHS=/workspace,/tmp
```

### Logging

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text
LOG_FILE=./logs/autoclaude.log
```

## Configuration Files

### config.yaml

Main configuration file:

```yaml
app:
  name: Auto-Claude
  version: 1.0.0
  environment: development  # development, staging, production

llm:
  default_provider: anthropic
  providers:
    anthropic:
      model: claude-sonnet-4-20250514
      max_tokens: 4096
      temperature: 0.7
    openai:
      model: gpt-4o
      max_tokens: 4096
      temperature: 0.7
    ollama:
      base_url: http://localhost:11434
      model: llama3.2

memory:
  backend: chromadb
  embedding:
    provider: openai
    model: text-embedding-3-small
  settings:
    persist_directory: ./data/chroma
    collection_name: memories

agents:
  default_config:
    max_iterations: 10
    timeout: 300
    retry_attempts: 3

tools:
  enabled:
    - filesystem
    - code
    - shell
  sandbox:
    enabled: true
    allowed_paths:
      - /workspace
      - /tmp
    blocked_commands:
      - rm -rf
      - sudo

security:
  auth:
    enabled: true
    method: jwt
  rate_limiting:
    enabled: true
    requests_per_minute: 60
  audit:
    enabled: true
    destination: file
```

### agents.yaml

Agent-specific configuration:

```yaml
agents:
  coder:
    provider: anthropic
    model: claude-sonnet-4-20250514
    capabilities:
      - python
      - typescript
      - rust
    config:
      max_tokens: 8192
      temperature: 0.3

  reviewer:
    provider: openai
    model: gpt-4o
    capabilities:
      - review
      - security
    config:
      max_tokens: 4096
      temperature: 0.5

  planner:
    provider: anthropic
    model: claude-sonnet-4-20250514
    capabilities:
      - planning
      - decomposition
    config:
      max_iterations: 20
```

### tools.yaml

Tool configuration:

```yaml
tools:
  filesystem:
    read_file:
      max_file_size: 10485760  # 10MB
      allowed_extensions:
        - .py
        - .ts
        - .md
        - .json
    write_file:
      backup_enabled: true
      backup_dir: ./backups

  code:
    search:
      max_results: 100
      include_hidden: false
    analyze:
      timeout: 60

  shell:
    allowed_commands:
      - git
      - npm
      - python
      - pytest
    blocked_patterns:
      - "rm -rf /"
      - "sudo"
    timeout: 30
```

## Programmatic Configuration

### Loading Configuration

```python
from apps.backend.config import Config, load_config

# Load from files
config = load_config(
    config_path="config.yaml",
    env_file=".env"
)

# Access values
provider = config.llm.default_provider
model = config.llm.providers[provider].model
```

### Runtime Configuration

```python
from apps.backend.config import RuntimeConfig

runtime = RuntimeConfig(
    debug=True,
    log_level="DEBUG",
    override_provider="ollama"
)

# Apply to application
app.configure(runtime)
```

### Environment-Specific Configuration

```python
from apps.backend.config import load_config

# Loads config.yaml and config.{environment}.yaml
config = load_config(environment="production")
```

## Provider Configuration

### Anthropic

```python
from apps.backend.llm import LLMProvider, ProviderConfig

provider = LLMProvider.create(
    provider_type="anthropic",
    config=ProviderConfig(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0.7
    )
)
```

### OpenAI

```python
provider = LLMProvider.create(
    provider_type="openai",
    config=ProviderConfig(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o",
        organization="org-xxx"  # Optional
    )
)
```

### Azure OpenAI

```python
provider = LLMProvider.create(
    provider_type="azure",
    config=ProviderConfig(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        model="gpt-4",  # Deployment name
        api_version="2024-02-15-preview"
    )
)
```

### Ollama (Local)

```python
provider = LLMProvider.create(
    provider_type="ollama",
    config=ProviderConfig(
        base_url="http://localhost:11434",
        model="llama3.2"
    )
)
```

## Memory Configuration

### In-Memory

```python
from apps.backend.memory import MemoryStore

store = MemoryStore(backend="in_memory")
```

### File-Based

```python
store = MemoryStore(
    backend="file",
    config={
        "path": "./data/memories",
        "format": "json"
    }
)
```

### ChromaDB

```python
store = MemoryStore(
    backend="chromadb",
    config={
        "persist_directory": "./data/chroma",
        "collection_name": "memories"
    },
    embedding_config=EmbeddingConfig(
        provider="openai",
        model="text-embedding-3-small"
    )
)
```

## Security Configuration

### Authentication

```yaml
security:
  auth:
    enabled: true
    method: jwt
    jwt:
      secret: ${JWT_SECRET}
      algorithm: HS256
      expiry_hours: 24
    oauth:
      enabled: false
      providers:
        - github
        - google
```

### Rate Limiting

```yaml
security:
  rate_limiting:
    enabled: true
    default:
      requests: 100
      window: 60
    endpoints:
      /api/generate:
        requests: 10
        window: 60
```

### Sandboxing

```yaml
security:
  sandbox:
    enabled: true
    paths:
      allowed:
        - /workspace
        - /tmp/agent-output
      blocked:
        - /etc
        - /var
        - ~/.ssh
    resources:
      max_memory_mb: 512
      max_cpu_seconds: 30
```

## Logging Configuration

### File Logging

```yaml
logging:
  level: INFO
  format: json
  handlers:
    file:
      enabled: true
      path: ./logs/autoclaude.log
      rotation:
        max_size: 10485760  # 10MB
        backup_count: 5
    console:
      enabled: true
      format: text
```

### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

## Best Practices

1. **Use environment variables** for secrets
2. **Separate configs** by environment
3. **Validate configuration** on startup
4. **Document all options** with defaults
5. **Use typed configuration** classes
6. **Log configuration** (without secrets) on startup

## See Also

- [Getting Started](getting-started.md)
- [Security Overview](../security/security-overview.md)
- [Deployment Guide](deployment.md)
