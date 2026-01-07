# LLM Provider API Reference

Complete API documentation for LLM provider integration.

## Overview

The LLM API provides a unified interface for interacting with multiple
language model providers including OpenAI, Anthropic, Azure, and local models.

## Supported Providers

| Provider | Models | Streaming | Embeddings |
|----------|--------|-----------|------------|
| `openai` | GPT-4o, GPT-4, GPT-3.5 | ✅ | ✅ |
| `anthropic` | Claude 3.5, Claude 3 | ✅ | ❌ |
| `azure` | Azure OpenAI models | ✅ | ✅ |
| `gemini` | Gemini Pro, Ultra | ✅ | ✅ |
| `ollama` | Llama, Mistral, etc. | ✅ | ✅ |
| `lmstudio` | Local models | ✅ | ✅ |
| `openrouter` | Multi-provider | ✅ | ❌ |
| `copilot` | GitHub Copilot | ✅ | ❌ |

## Core Classes

### LLMProvider

Base interface for all providers.

```python
from apps.backend.llm import LLMProvider, ProviderConfig

provider = LLMProvider.create(
    provider_type="anthropic",
    config=ProviderConfig(
        api_key="your-api-key",
        model="claude-sonnet-4-20250514",
        max_tokens=4096
    )
)
```

#### Methods

##### complete

Generate a completion.

```python
response = await provider.complete(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Python decorators."}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.content)
print(f"Tokens used: {response.usage.total_tokens}")
```

##### stream

Stream a completion.

```python
async for chunk in provider.stream(messages):
    print(chunk.content, end="", flush=True)
```

##### embed

Generate embeddings (where supported).

```python
embeddings = await provider.embed(
    texts=["Hello world", "Python programming"],
    model="text-embedding-3-small"
)
```

### ProviderConfig

Configuration for a provider.

```python
@dataclass
class ProviderConfig:
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    retry_attempts: int = 3
```

### CompletionResponse

Response from a completion request.

```python
@dataclass
class CompletionResponse:
    content: str
    model: str
    usage: TokenUsage
    finish_reason: str
    metadata: dict
```

### TokenUsage

Token usage statistics.

```python
@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

## Provider-Specific Configuration

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

### Anthropic

```python
provider = LLMProvider.create(
    provider_type="anthropic",
    config=ProviderConfig(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="claude-sonnet-4-20250514",
        max_tokens=8192
    )
)
```

### Azure OpenAI

```python
provider = LLMProvider.create(
    provider_type="azure",
    config=ProviderConfig(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        base_url="https://your-resource.openai.azure.com",
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

### LM Studio (Local)

```python
provider = LLMProvider.create(
    provider_type="lmstudio",
    config=ProviderConfig(
        base_url="http://localhost:1234/v1",
        model="local-model"
    )
)
```

### Google Gemini

```python
provider = LLMProvider.create(
    provider_type="gemini",
    config=ProviderConfig(
        api_key=os.environ["GOOGLE_API_KEY"],
        model="gemini-pro"
    )
)
```

### OpenRouter

```python
provider = LLMProvider.create(
    provider_type="openrouter",
    config=ProviderConfig(
        api_key=os.environ["OPENROUTER_API_KEY"],
        model="anthropic/claude-3.5-sonnet"
    )
)
```

## Provider Registry

Manage multiple providers.

```python
from apps.backend.llm import ProviderRegistry

registry = ProviderRegistry()

# Register providers
registry.register("primary", anthropic_provider)
registry.register("fallback", openai_provider)
registry.register("local", ollama_provider)

# Get provider
provider = registry.get("primary")

# List all
providers = registry.list_all()
```

## Fallback Configuration

Configure automatic fallback to alternative providers.

```python
from apps.backend.llm import FallbackProvider

fallback = FallbackProvider(
    providers=[
        ("anthropic", anthropic_provider),
        ("openai", openai_provider),
        ("ollama", ollama_provider)
    ],
    fallback_on=[RateLimitError, ServiceUnavailableError]
)

# Will automatically try next provider on failure
response = await fallback.complete(messages)
```

## Rate Limiting

Built-in rate limiting support.

```python
provider = LLMProvider.create(
    provider_type="openai",
    config=ProviderConfig(
        api_key=api_key,
        model="gpt-4o",
        rate_limit=RateLimitConfig(
            requests_per_minute=60,
            tokens_per_minute=90000
        )
    )
)
```

## Caching

Enable response caching for repeated queries.

```python
from apps.backend.llm import CachedProvider

cached = CachedProvider(
    provider=base_provider,
    cache_backend="redis",
    ttl=3600  # 1 hour
)
```

## Error Handling

### Exception Types

| Exception | Description |
|-----------|-------------|
| `ProviderError` | Base provider exception |
| `AuthenticationError` | Invalid API key |
| `RateLimitError` | Rate limit exceeded |
| `ModelNotFoundError` | Invalid model ID |
| `ContextLengthError` | Input too long |
| `ContentFilterError` | Content policy violation |

### Error Handling Example

```python
from apps.backend.llm.exceptions import (
    RateLimitError,
    ContextLengthError
)

try:
    response = await provider.complete(messages)
except RateLimitError as e:
    await asyncio.sleep(e.retry_after)
    response = await provider.complete(messages)
except ContextLengthError:
    # Truncate messages and retry
    messages = truncate_messages(messages)
    response = await provider.complete(messages)
```

## Monitoring

Track provider usage and performance.

```python
# Get usage statistics
stats = provider.get_stats()
print(f"Requests: {stats.total_requests}")
print(f"Tokens: {stats.total_tokens}")
print(f"Avg latency: {stats.avg_latency_ms}ms")

# Enable detailed logging
provider.set_logging(level="DEBUG")
```

## Best Practices

1. **Use environment variables** - Never hardcode API keys
2. **Configure fallbacks** - Handle provider failures gracefully
3. **Set appropriate timeouts** - Prevent hanging requests
4. **Monitor usage** - Track costs and performance
5. **Cache when possible** - Reduce API calls for repeated queries
6. **Handle rate limits** - Implement exponential backoff

## See Also

- [Agent API](agent-api.md)
- [LLM Configuration Guide](../guides/llm-configuration.md)
- [Provider Selection Guide](../guides/provider-selection.md)
