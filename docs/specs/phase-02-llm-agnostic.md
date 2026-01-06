# Phase 2: LLM Agnostic Layer

> **Duration**: Week 3-4 | **Priority**: ⚠️ CRITICAL
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| LLMProvider abstraction works | All 8 providers implement interface | 100% |
| Router routes correctly | Requests go to configured provider | ✅ |
| Per-agent config works | Different agents use different LLMs | ✅ |
| Failover functional | Auto-switch on provider failure | ✅ |
| No provider hardcoded | Code review passes | ✅ |
| All providers equal | No "primary" designation | ✅ |

### Deliverables

1. `apps/backend/llm/abstraction/base_provider.py`
2. `apps/backend/llm/abstraction/message.py`
3. `apps/backend/llm/abstraction/response.py`
4. `apps/backend/llm/providers/` (8 provider implementations)
5. `apps/backend/llm/router/router.py`
6. `apps/backend/llm/config/agent_llm_config.py`
7. Unit tests for all modules

---

## Section 1: LLM Abstraction Layer

### Task 1.1: Create LLM Directory Structure

**Steps**:
1. Create `apps/backend/llm/` directory
2. Create subdirectories: `abstraction/`, `providers/`, `router/`, `config/`
3. Create `__init__.py` in each

**Directory Structure**:
```
apps/backend/llm/
├── __init__.py
├── abstraction/
│   ├── __init__.py
│   ├── base_provider.py
│   ├── message.py
│   └── response.py
├── providers/
│   ├── __init__.py
│   ├── copilot_provider.py
│   ├── openrouter_provider.py
│   ├── ollama_provider.py
│   ├── lmstudio_provider.py
│   ├── gemini_provider.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── azure_provider.py
├── router/
│   ├── __init__.py
│   ├── router.py
│   ├── health.py
│   └── failover.py
└── config/
    ├── __init__.py
    └── agent_llm_config.py
```

---

### Task 1.2: Create Message Model

**File**: `apps/backend/llm/abstraction/message.py`

```python
"""Provider-agnostic message format."""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class Message:
    """Universal message format for all providers."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result
```

---

### Task 1.3: Create Response Model

**File**: `apps/backend/llm/abstraction/response.py`

```python
"""Provider-agnostic response format."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

@dataclass
class LLMResponse:
    """Universal response format from all providers."""
    content: str
    provider: str               # Which provider was used
    model: str                  # Which model was used
    usage: TokenUsage = None
    finish_reason: str = "stop"
    latency_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = TokenUsage()
```

---

### Task 1.4: Create Base Provider

**File**: `apps/backend/llm/abstraction/base_provider.py`

```python
"""Abstract base class for ALL LLM providers.

CRITICAL: All providers are EQUAL. No primary/fallback designation.
Users choose their preferred providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .message import Message
from .response import LLMResponse

class ProviderStatus(Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNCONFIGURED = "unconfigured"

@dataclass
class ModelInfo:
    """Information about an available model."""
    id: str
    name: str
    provider: str
    context_length: int = 4096
    supports_tools: bool = True
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0

@dataclass
class ProviderHealth:
    """Provider health status."""
    status: ProviderStatus
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    last_checked: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base for ALL LLM providers.
    
    ALL PROVIDERS ARE EQUAL - no favorites.
    Users configure their preferred providers.
    """
    
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self._configured = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure provider with credentials.
        
        Args:
            config: Provider-specific configuration
            
        Returns:
            True if configuration successful
        """
        pass
    
    @abstractmethod
    async def complete(
        self, 
        messages: List[Message],
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion.
        
        Args:
            messages: Conversation messages
            model: Optional model override
            **kwargs: Additional parameters
            
        Returns:
            Provider-agnostic response
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider."""
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider availability."""
        pass
    
    @property
    def is_configured(self) -> bool:
        """Whether provider has been configured."""
        return self._configured
```

---

## Section 2: Provider Implementations

### Task 2.1: OpenRouter Provider

**File**: `apps/backend/llm/providers/openrouter_provider.py`

**Key Features**:
- Access to 100+ models
- Single API key for multiple providers
- Cost-effective routing

---

### Task 2.2: Ollama Provider

**File**: `apps/backend/llm/providers/ollama_provider.py`

**Key Features**:
- Local model execution
- No API key required
- Privacy-focused

---

### Task 2.3: OpenAI Provider

**File**: `apps/backend/llm/providers/openai_provider.py`

**Key Features**:
- GPT-4, GPT-4o models
- Direct API access

---

### Task 2.4: Anthropic Provider

**File**: `apps/backend/llm/providers/anthropic_provider.py`

**Key Features**:
- Claude models
- Extended thinking support

---

### Task 2.5: Gemini Provider

**File**: `apps/backend/llm/providers/gemini_provider.py`

**Key Features**:
- Google Gemini models
- Long context support

---

### Task 2.6: Copilot Provider

**File**: `apps/backend/llm/providers/copilot_provider.py`

**Key Features**:
- VS Code LM API integration
- GitHub authentication

---

### Task 2.7: LM Studio Provider

**File**: `apps/backend/llm/providers/lmstudio_provider.py`

**Key Features**:
- OpenAI-compatible API
- Local model hosting

---

### Task 2.8: Azure Provider

**File**: `apps/backend/llm/providers/azure_provider.py`

**Key Features**:
- Enterprise Azure OpenAI
- Regional endpoints

---

## Section 3: LLM Router

### Task 3.1: Implement Router

**File**: `apps/backend/llm/router/router.py`

```python
"""LLM Router - Routes requests to user-configured providers."""
from typing import Dict, Optional, List
from ..abstraction.base_provider import LLMProvider, ProviderHealth, ProviderStatus
from ..abstraction.message import Message
from ..abstraction.response import LLMResponse
from ..config.agent_llm_config import AgentLLMConfig

class ProviderNotConfigured(Exception):
    """Raised when requested provider is not configured."""
    pass

class AllProvidersUnavailable(Exception):
    """Raised when all providers in fallback chain fail."""
    pass


class LLMRouter:
    """Routes LLM requests to user-configured providers.
    
    NO DEFAULT PROVIDER - Users must configure at least one.
    All providers are treated equally.
    """
    
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
    
    def register_provider(self, provider: LLMProvider) -> None:
        """Register a configured provider."""
        self._providers[provider.provider_id] = provider
    
    def get_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """Get provider by ID."""
        return self._providers.get(provider_id)
    
    def list_providers(self) -> List[str]:
        """List all registered provider IDs."""
        return list(self._providers.keys())
    
    async def route(
        self,
        messages: List[Message],
        config: AgentLLMConfig,
        **kwargs
    ) -> LLMResponse:
        """Route request to configured provider with failover.
        
        Args:
            messages: Conversation messages
            config: Agent's LLM configuration
            **kwargs: Additional parameters
            
        Returns:
            LLM response from successful provider
            
        Raises:
            ProviderNotConfigured: If primary provider not registered
            AllProvidersUnavailable: If all providers fail
        """
        # Try primary provider
        provider = self._providers.get(config.provider)
        if not provider:
            raise ProviderNotConfigured(
                f"Provider '{config.provider}' not configured. "
                f"Available: {self.list_providers()}"
            )
        
        try:
            return await provider.complete(
                messages, 
                model=config.model,
                **kwargs
            )
        except Exception as primary_error:
            # Try fallback chain
            for fallback_id in (config.fallback_providers or []):
                fallback = self._providers.get(fallback_id)
                if fallback:
                    try:
                        return await fallback.complete(messages, **kwargs)
                    except Exception:
                        continue
            
            # All failed
            raise AllProvidersUnavailable(
                f"Primary provider '{config.provider}' failed: {primary_error}. "
                f"All fallback providers also failed."
            )
    
    async def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Check health of all registered providers."""
        results = {}
        for provider_id, provider in self._providers.items():
            results[provider_id] = await provider.health_check()
        return results
```

---

### Task 3.2: Implement Health Monitor

**File**: `apps/backend/llm/router/health.py`

---

### Task 3.3: Implement Failover Logic

**File**: `apps/backend/llm/router/failover.py`

---

## Section 4: Agent LLM Configuration

### Task 4.1: Create Config Manager

**File**: `apps/backend/llm/config/agent_llm_config.py`

```python
"""Per-agent LLM configuration management."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
from pathlib import Path

@dataclass
class AgentLLMConfig:
    """Configuration for an agent's LLM provider.
    
    Each agent can use a DIFFERENT provider/model.
    """
    agent_id: str
    provider: str                              # User-chosen provider
    model: str                                 # User-chosen model
    fallback_providers: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_budget_daily: Optional[float] = None  # Optional daily limit
    enabled: bool = True


class AgentLLMConfigManager:
    """Manages per-agent LLM configurations."""
    
    def __init__(self, config_path: str = "agent_llm_configs.json"):
        self.config_path = Path(config_path)
        self._configs: Dict[str, AgentLLMConfig] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configurations from file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
                for agent_id, config_data in data.items():
                    self._configs[agent_id] = AgentLLMConfig(
                        agent_id=agent_id,
                        **config_data
                    )
    
    def _save(self) -> None:
        """Save configurations to file."""
        data = {}
        for agent_id, config in self._configs.items():
            data[agent_id] = {
                "provider": config.provider,
                "model": config.model,
                "fallback_providers": config.fallback_providers,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "cost_budget_daily": config.cost_budget_daily,
                "enabled": config.enabled,
            }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def get(self, agent_id: str) -> Optional[AgentLLMConfig]:
        """Get config for agent."""
        return self._configs.get(agent_id)
    
    def set(self, config: AgentLLMConfig) -> None:
        """Set or update agent config."""
        self._configs[config.agent_id] = config
        self._save()
    
    def list_all(self) -> Dict[str, AgentLLMConfig]:
        """Get all configurations."""
        return self._configs.copy()
```

---

## Validation Checklist

- [ ] All 8 provider classes implement LLMProvider
- [ ] Router correctly routes to configured provider
- [ ] Failover works when primary fails
- [ ] Per-agent config persists correctly
- [ ] No provider is hardcoded as default
- [ ] All providers treated equally
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1 (Foundation)

**Enables**: Phase 3 (Authentication), Phase 4 (Orchestration)

---

## ADR References

- ADR-005: LLM-Agnostic Architecture
- ADR-013: Per-Agent LLM Configuration

---

*Phase 2 Specification v1.0.0*
