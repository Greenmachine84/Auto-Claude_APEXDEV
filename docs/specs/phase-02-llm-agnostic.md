# Phase 2: LLM Agnostic Layer

> **Duration**: Week 3-4 | **Priority**: ⚠️ CRITICAL
>
> **Status**: 📋 Specification Ready

---

## ⚠️ QUALITY STANDARDS

> **ALL implementations in this phase MUST meet these mandatory standards:**

| Standard | Requirement | Verification |
|----------|-------------|--------------|
| **World-Class** | Industry-leading LLM abstraction patterns | Architecture review |
| **Enterprise-Grade** | Production-ready from day one, handles edge cases | Load testing |
| **Fully Production Ready** | Zero technical debt, comprehensive error handling | Audit |
| **Clean & Concise Code** | Self-documenting, minimal complexity, DRY principles | Linting + Review |
| **Beyond PhD Level** | State-of-the-art distributed systems principles | Architecture review |

---

## Outcome Expectations

### Business Objective

| Objective | Description | Impact |
|-----------|-------------|--------|
| **Provider Independence** | Complete freedom from LLM vendor lock-in | User choice & flexibility |
| **Cost Optimization** | Users can select most cost-effective providers | Reduced operational costs |
| **Reliability** | Automatic failover ensures continuous operation | 99.9% availability target |
| **Future-Proofing** | New providers can be added without core changes | Long-term sustainability |

### Technical Outcome

| Outcome | Description | Measurement |
|---------|-------------|-------------|
| **LLM Abstraction Layer** | Provider-agnostic interface for all LLM operations | All 8 providers implement interface |
| **Intelligent Router** | Routes requests based on config with automatic failover | Failover in <500ms |
| **Per-Agent Configuration** | Each agent independently configurable for any provider | Config stored and applied |
| **Health Monitoring** | Real-time provider health with automatic degradation handling | Continuous health checks |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| LLMProvider abstraction works | All 8 providers implement interface | 100% | Uniform API across all providers |
| Router routes correctly | Requests go to configured provider | ✅ | Zero misroutes |
| Per-agent config works | Different agents use different LLMs | ✅ | Hot-swappable at runtime |
| Failover functional | Auto-switch on provider failure | ✅ | <500ms failover time |
| No provider hardcoded | Code review passes | ✅ | Zero hardcoded strings |
| All providers equal | No "primary" designation | ✅ | Equal weight in routing |
| Response normalization | Consistent response format | ✅ | Provider-agnostic outputs |
| Cost tracking accurate | Token usage tracked per provider | ✅ | <1% variance from actual |

### Acceptance Tests

| Test | Input | Expected Output | Passing Criteria |
|------|-------|-----------------|------------------|
| AT-2.1 | Import all providers | No errors | All 8 providers importable |
| AT-2.2 | Configure OpenRouter | Configuration success | API key validated |
| AT-2.3 | Configure Ollama (local) | Configuration success | Endpoint reachable |
| AT-2.4 | Route to configured provider | Response from correct provider | Provider ID in response |
| AT-2.5 | Provider fails mid-request | Automatic failover | Response from fallback |
| AT-2.6 | All providers unavailable | Graceful error | AllProvidersUnavailable exception |
| AT-2.7 | Agent A uses OpenRouter, Agent B uses Ollama | Both work independently | Correct provider per agent |
| AT-2.8 | Health check all providers | Status per provider | Accurate availability status |
| AT-2.9 | List models per provider | Model catalog | Provider-specific models listed |
| AT-2.10 | Cost estimation | Token/cost calculation | Accurate to <5% |

### Performance Metrics

| Metric | Target | World-Class Standard |
|--------|--------|----------------------|
| Router overhead | <5ms | Negligible latency impact |
| Provider initialization | <100ms | Fast startup |
| Failover time | <500ms | Seamless user experience |
| Health check latency | <50ms | Real-time monitoring |
| Concurrent requests | 100+ | Horizontally scalable |
| Memory per provider | <10MB | Efficient resource usage |
| Configuration reload | <1s | No downtime for config changes |

### Risk Mitigations

| Risk | Mitigation | Verification |
|------|------------|--------------|
| Provider API changes | Version pinning + abstraction layer | Integration test suite |
| Rate limiting | Per-provider rate limit tracking | Automatic backoff tests |
| Credential exposure | Encrypted credential storage | Security audit |
| Network failures | Exponential backoff + circuit breaker | Chaos testing |
| Model deprecation | Model catalog auto-refresh | Deprecation detection |
| Cost overruns | Per-agent budget limits | Budget enforcement tests |

### Integration Points

| Phase | Component | Integration |
|-------|-----------|-------------|
| Phase 1 | BaseEnterpriseAgent | Uses AgentLLMConfig from this phase |
| Phase 1 | EpisodeStore | Stores llm_provider/llm_model per episode |
| Phase 3 | Auth | User credentials link to provider configs |
| Phase 7 | Enterprise Agents | All agents use LLM router |
| Phase 8 | Analytics | Cost tracking data feeds analytics |

### User-Visible Impact

| Impact | Description |
|--------|-------------|
| **Provider Choice** | Users can select from 8 equal LLM providers |
| **Per-Agent Customization** | Assign different models to different agents |
| **Cost Control** | Set budgets per agent/provider |
| **No Lock-In** | Switch providers without code changes |
| **Reliability** | Automatic failover prevents downtime |

### Deliverables

| # | Deliverable | Purpose | LOC Estimate |
|---|-------------|---------|--------------|
| 1 | `apps/backend/llm/abstraction/base_provider.py` | Abstract LLM interface | 200-250 |
| 2 | `apps/backend/llm/abstraction/message.py` | Universal message format | 50-80 |
| 3 | `apps/backend/llm/abstraction/response.py` | Universal response format | 80-100 |
| 4 | `apps/backend/llm/providers/copilot_provider.py` | GitHub Copilot integration | 200-250 |
| 5 | `apps/backend/llm/providers/openrouter_provider.py` | OpenRouter multi-model | 200-250 |
| 6 | `apps/backend/llm/providers/ollama_provider.py` | Local Ollama models | 200-250 |
| 7 | `apps/backend/llm/providers/lmstudio_provider.py` | LM Studio local | 150-200 |
| 8 | `apps/backend/llm/providers/gemini_provider.py` | Google Gemini | 200-250 |
| 9 | `apps/backend/llm/providers/openai_provider.py` | OpenAI direct | 200-250 |
| 10 | `apps/backend/llm/providers/anthropic_provider.py` | Anthropic direct | 200-250 |
| 11 | `apps/backend/llm/providers/azure_provider.py` | Azure OpenAI | 200-250 |
| 12 | `apps/backend/llm/router/router.py` | Intelligent routing | 300-400 |
| 13 | `apps/backend/llm/router/health.py` | Health monitoring | 150-200 |
| 14 | `apps/backend/llm/router/failover.py` | Failover logic | 150-200 |
| 15 | `apps/backend/llm/config/agent_llm_config.py` | Per-agent configuration | 200-250 |
| 16 | Unit tests for all modules | Test coverage | 1000+ |

---

## Section 1: LLM Abstraction Layer

### Task 1.1: Create LLM Directory Structure

**Objective**: Establish clean directory structure for LLM abstraction

**Quality Gate**: Follows Python package best practices, no circular imports

**Steps**:

| Step | Action | Verification |
|------|--------|--------------|
| 1.1.1 | Create `apps/backend/llm/` directory | `test -d` passes |
| 1.1.2 | Create subdirectories: `abstraction/`, `providers/`, `router/`, `config/` | All exist |
| 1.1.3 | Create `__init__.py` in each directory | All have exports |
| 1.1.4 | Verify no circular imports | Import test passes |

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

**Expected Outcome**: Clean, organized package structure ready for world-class LLM abstraction.

---

### Task 1.2: Create Message Model

**Objective**: Create provider-agnostic message format

**Quality Gate**: Serializable, immutable, fully typed

**File**: `apps/backend/llm/abstraction/message.py`

```python
"""Provider-Agnostic Message Format - World-Class Abstraction.

This module defines the universal message format used across ALL
LLM providers, ensuring complete provider independence.

Design Principles:
    - Immutable after creation (dataclass frozen)
    - Serializable to any format
    - Complete type safety
    - Provider-agnostic field names

Quality Standards:
    - 100% type annotated
    - Full PEP 257 docstrings
    - Serialization tested
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json

class MessageRole(Enum):
    """Standardized message roles across all providers.
    
    Maps to provider-specific roles during serialization.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"  # Legacy support

@dataclass(frozen=True)
class ToolCall:
    """Tool/function call from assistant.
    
    Represents a request to execute a tool.
    """
    id: str
    name: str
    arguments: str  # JSON string

@dataclass(frozen=True)
class Message:
    """Universal message format for ALL providers.
    
    This is the single source of truth for message representation.
    All providers must serialize to/from this format.
    
    Attributes:
        role: Message sender role
        content: Message text content
        name: Optional sender name (for tool responses)
        tool_call_id: ID of tool call being responded to
        tool_calls: List of tool calls (if role is assistant)
        metadata: Additional provider-specific data
        
    Example:
        >>> msg = Message(
        ...     role=MessageRole.USER,
        ...     content="Analyze this code for security issues"
        ... )
        >>> serialized = msg.to_dict()
    """
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls.
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        result: Dict[str, Any] = {
            "role": self.role.value, 
            "content": self.content
        }
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            result["tool_calls"] = [
                {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                for tc in self.tool_calls
            ]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary.
        
        Args:
            data: Dictionary with message data
            
        Returns:
            Message instance
        """
        tool_calls = None
        if "tool_calls" in data:
            tool_calls = [
                ToolCall(id=tc["id"], name=tc["name"], arguments=tc["arguments"])
                for tc in data["tool_calls"]
            ]
        
        return cls(
            role=MessageRole(data["role"]),
            content=data.get("content", ""),
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            tool_calls=tool_calls,
            metadata=data.get("metadata", {}),
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Conversation:
    """Collection of messages forming a conversation.
    
    Provides utilities for managing message history.
    """
    messages: List[Message] = field(default_factory=list)
    
    def add(self, message: Message) -> None:
        """Add message to conversation."""
        self.messages.append(message)
    
    def add_user(self, content: str) -> None:
        """Add user message."""
        self.add(Message(role=MessageRole.USER, content=content))
    
    def add_assistant(self, content: str) -> None:
        """Add assistant message."""
        self.add(Message(role=MessageRole.ASSISTANT, content=content))
    
    def add_system(self, content: str) -> None:
        """Add system message."""
        self.add(Message(role=MessageRole.SYSTEM, content=content))
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all messages to list of dicts."""
        return [m.to_dict() for m in self.messages]
    
    def token_estimate(self) -> int:
        """Rough estimate of token count.
        
        Uses ~4 chars per token heuristic.
        """
        total_chars = sum(len(m.content) for m in self.messages)
        return total_chars // 4
```

**Validation Checklist**:
- [ ] MessageRole enum covers all roles
- [ ] Message is immutable (frozen=True)
- [ ] to_dict/from_dict round-trip works
- [ ] JSON serialization works
- [ ] Type hints validate with mypy
- [ ] Docstrings complete

**Expected Outcome**: Universal message format that works with any LLM provider.

---

### Task 1.3: Create Response Model

**Objective**: Create provider-agnostic response format

**Quality Gate**: Captures all relevant metadata, serializable, typed

**File**: `apps/backend/llm/abstraction/response.py`

```python
"""Provider-Agnostic Response Format - Enterprise-Grade Abstraction.

This module defines the universal response format returned from ALL
LLM providers, ensuring consistent handling regardless of provider.

Design Principles:
    - Complete response metadata capture
    - Cost tracking integration
    - Performance metrics included
    - Provider attribution maintained

Quality Standards:
    - 100% type annotated
    - Comprehensive error handling
    - Full audit trail support
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class TokenUsage:
    """Token usage tracking with cost estimation.
    
    Captures complete token usage for cost tracking and analytics.
    
    Attributes:
        prompt_tokens: Tokens in the input
        completion_tokens: Tokens in the output
        total_tokens: Sum of prompt + completion
        cached_tokens: Tokens served from cache (if supported)
        estimated_cost: Cost in USD (if calculable)
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    estimated_cost: Optional[float] = None
    
    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens

@dataclass
class ToolCallResult:
    """Result of a tool call in the response."""
    id: str
    name: str
    arguments: str  # JSON string

@dataclass
class LLMResponse:
    """Universal response format from ALL providers.
    
    This is the single source of truth for LLM response representation.
    All providers must normalize their responses to this format.
    
    World-Class Features:
    - Complete provider attribution
    - Detailed performance metrics
    - Full token/cost tracking
    - Error details when applicable
    - Raw response preservation for debugging
    
    Attributes:
        content: Generated text response
        provider: Provider that generated response
        model: Model that generated response
        usage: Token usage statistics
        finish_reason: Why generation stopped
        latency_ms: Response time in milliseconds
        success: Whether generation succeeded
        error: Error message if failed
        tool_calls: Tool calls if any
        raw_response: Original provider response (for debugging)
        request_id: Unique request identifier
        created_at: Timestamp of response
        
    Example:
        >>> response = LLMResponse(
        ...     content="Analysis complete. No issues found.",
        ...     provider="openrouter",
        ...     model="anthropic/claude-3-opus",
        ...     usage=TokenUsage(prompt_tokens=100, completion_tokens=50)
        ... )
    """
    content: str
    provider: str
    model: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    latency_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    tool_calls: Optional[List[ToolCallResult]] = None
    raw_response: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
    
    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return bool(self.tool_calls)
    
    @property
    def is_truncated(self) -> bool:
        """Check if response was truncated due to token limit."""
        return self.finish_reason in ["length", "max_tokens"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
                "estimated_cost": self.usage.estimated_cost,
            },
            "finish_reason": self.finish_reason,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "request_id": self.request_id,
            "created_at": self.created_at,
        }


@dataclass
class StreamChunk:
    """Chunk from streaming response.
    
    Used for real-time streaming from providers that support it.
    """
    content: str
    provider: str
    model: str
    is_final: bool = False
    finish_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None
```

**Validation Checklist**:
- [ ] TokenUsage calculates total correctly
- [ ] LLMResponse captures all metadata
- [ ] to_dict serialization works
- [ ] StreamChunk supports streaming
- [ ] All type hints validate

**Expected Outcome**: Complete response abstraction that preserves all provider information.

---

### Task 1.4: Create Base Provider

**Objective**: Define abstract interface for ALL LLM providers

**Quality Gate**: Complete abstraction, no provider-specific assumptions

**File**: `apps/backend/llm/abstraction/base_provider.py`

```python
"""Abstract Base Class for ALL LLM Providers - Enterprise-Grade Abstraction.

CRITICAL DESIGN PRINCIPLE:
    ALL PROVIDERS ARE EQUAL. There is NO default provider.
    Users MUST explicitly configure their preferred providers.
    The system makes NO assumptions about which provider to use.

This module defines the contract that ALL LLM providers must implement,
ensuring complete provider independence and substitutability.

Design Patterns:
    - Strategy Pattern: Providers are interchangeable strategies
    - Template Method: Common workflow with provider-specific details
    - Factory Pattern: Provider instances created through registry

Quality Standards:
    - 100% type annotated
    - Complete async/await support
    - Comprehensive error handling
    - Full logging integration
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import logging

from .message import Message
from .response import LLMResponse, StreamChunk, TokenUsage

logger = logging.getLogger(__name__)

class ProviderStatus(Enum):
    """Provider operational status.
    
    Used for health monitoring and routing decisions.
    """
    AVAILABLE = "available"      # Fully operational
    DEGRADED = "degraded"        # Partially functional
    UNAVAILABLE = "unavailable"  # Completely down
    UNCONFIGURED = "unconfigured"  # Not yet configured
    RATE_LIMITED = "rate_limited"  # Temporarily throttled

@dataclass
class ModelInfo:
    """Information about an available model.
    
    Captures model capabilities and pricing for intelligent routing.
    
    Attributes:
        id: Model identifier (provider-specific)
        name: Human-readable model name
        provider: Provider offering this model
        context_length: Maximum context window in tokens
        supports_tools: Whether function calling is supported
        supports_vision: Whether image input is supported
        supports_streaming: Whether streaming responses work
        cost_per_1k_input: Cost in USD per 1000 input tokens
        cost_per_1k_output: Cost in USD per 1000 output tokens
        max_output_tokens: Maximum output tokens (if limited)
    """
    id: str
    name: str
    provider: str
    context_length: int = 4096
    supports_tools: bool = True
    supports_vision: bool = False
    supports_streaming: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    max_output_tokens: Optional[int] = None

@dataclass
class ProviderHealth:
    """Provider health status with diagnostics.
    
    Attributes:
        status: Current operational status
        latency_ms: Last response latency
        error: Error message if unhealthy
        last_checked: ISO timestamp of last check
        consecutive_failures: Number of failures in a row
        requests_today: Total requests today
        errors_today: Total errors today
    """
    status: ProviderStatus
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    last_checked: Optional[str] = None
    consecutive_failures: int = 0
    requests_today: int = 0
    errors_today: int = 0
    
    @property
    def error_rate(self) -> float:
        """Calculate today's error rate."""
        if self.requests_today == 0:
            return 0.0
        return self.errors_today / self.requests_today


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass

class ProviderNotConfiguredError(LLMProviderError):
    """Raised when provider is not configured."""
    pass

class ProviderUnavailableError(LLMProviderError):
    """Raised when provider is unavailable."""
    pass

class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

class ModelNotFoundError(LLMProviderError):
    """Raised when requested model is not available."""
    pass


class LLMProvider(ABC):
    """Abstract base for ALL LLM providers.
    
    ⚠️ CRITICAL DESIGN PRINCIPLES:
    
    1. ALL PROVIDERS ARE EQUAL
       - No provider is designated as "primary" or "default"
       - Users explicitly choose their providers
       - Routing is purely based on user configuration
    
    2. COMPLETE ABSTRACTION
       - Uniform API across all providers
       - Provider-specific details hidden
       - Responses normalized to common format
    
    3. PRODUCTION-READY
       - Comprehensive error handling
       - Retry logic with exponential backoff
       - Rate limit awareness
       - Health monitoring
    
    4. OBSERVABLE
       - All operations logged
       - Metrics collection ready
       - Debug information preserved
    
    Implementation Contract:
        Subclasses MUST implement:
        - name property
        - configure() method
        - complete() method
        - list_models() method
        - health_check() method
        
        Subclasses MAY override:
        - stream() method (default raises NotImplementedError)
        - estimate_cost() method
        
    Example:
        >>> class MyProvider(LLMProvider):
        ...     @property
        ...     def name(self) -> str:
        ...         return "MyProvider"
        ...     
        ...     async def configure(self, config: Dict[str, Any]) -> bool:
        ...         self.api_key = config.get("api_key")
        ...         self._configured = bool(self.api_key)
        ...         return self._configured
        ...     
        ...     # ... implement other abstract methods
    """
    
    def __init__(self, provider_id: str):
        """Initialize provider.
        
        Args:
            provider_id: Unique identifier for this provider instance
        """
        self.provider_id = provider_id
        self._configured = False
        self._health = ProviderHealth(status=ProviderStatus.UNCONFIGURED)
        self._request_count = 0
        self._error_count = 0
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name.
        
        Returns:
            Display name like "OpenRouter" or "Ollama"
        """
        pass
    
    @property
    def is_configured(self) -> bool:
        """Whether provider has been configured with credentials."""
        return self._configured
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure provider with credentials and settings.
        
        Args:
            config: Provider-specific configuration dictionary
                Common keys:
                - api_key: API key for authentication
                - base_url: Custom API endpoint
                - organization: Organization ID (if applicable)
                - timeout: Request timeout in seconds
                
        Returns:
            True if configuration successful, False otherwise
            
        Raises:
            ValueError: If required config is missing
        """
        pass
    
    @abstractmethod
    async def complete(
        self, 
        messages: List[Message],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from messages.
        
        This is the core method that all providers must implement.
        
        Args:
            messages: List of conversation messages
            model: Model to use (provider-specific ID)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            tools: Tool/function definitions for function calling
            **kwargs: Provider-specific additional parameters
            
        Returns:
            Normalized LLMResponse with generated content
            
        Raises:
            ProviderNotConfiguredError: If not configured
            ProviderUnavailableError: If provider is down
            RateLimitError: If rate limit exceeded
            ModelNotFoundError: If model doesn't exist
        """
        pass
    
    async def stream(
        self, 
        messages: List[Message],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream completion response.
        
        Default implementation raises NotImplementedError.
        Override in providers that support streaming.
        
        Args:
            messages: List of conversation messages
            model: Model to use
            **kwargs: Additional parameters
            
        Yields:
            StreamChunk objects as they arrive
        """
        raise NotImplementedError(
            f"{self.name} does not support streaming. "
            f"Use complete() instead."
        )
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider.
        
        Returns:
            List of ModelInfo with capabilities and pricing
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider availability.
        
        Performs a lightweight check to verify the provider is responsive.
        Should complete in <1 second.
        
        Returns:
            ProviderHealth with current status
        """
        pass
    
    def estimate_cost(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str
    ) -> Optional[float]:
        """Estimate cost in USD for token usage.
        
        Default implementation returns None.
        Override in providers with known pricing.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model used
            
        Returns:
            Estimated cost in USD, or None if unknown
        """
        return None
    
    def _update_stats(self, success: bool) -> None:
        """Update internal statistics."""
        self._request_count += 1
        if not success:
            self._error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics.
        
        Returns:
            Dictionary with request/error counts and health
        """
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "configured": self._configured,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "health": self._health.status.value,
        }
```

**Validation Checklist**:
- [ ] Abstract methods defined completely
- [ ] No provider-specific assumptions
- [ ] All 8 providers can implement interface
- [ ] Streaming support defined
- [ ] Error hierarchy complete
- [ ] Health monitoring integrated

**Expected Outcome**: Rock-solid abstraction that ensures true LLM-agnosticism.

---

## Section 2: Provider Implementations

### Task 2.1: OpenRouter Provider

**Objective**: Implement OpenRouter provider for multi-model access

**Quality Gate**: Access to 100+ models, consistent API, error handling

**File**: `apps/backend/llm/providers/openrouter_provider.py`

**Key Features**:
- Access to 100+ models through single API
- Dynamic model listing from API
- Cost tracking with OpenRouter pricing
- Automatic fallback support

---

### Task 2.2: Ollama Provider

**Objective**: Implement Ollama provider for local model execution

**Quality Gate**: Local execution, no external API calls, privacy-focused

**File**: `apps/backend/llm/providers/ollama_provider.py`

**Key Features**:
- Local model execution
- No API key required
- Model pulling support
- GPU acceleration detection

---

### Task 2.3: OpenAI Provider

**Objective**: Implement direct OpenAI API access

**Quality Gate**: Full OpenAI API support, function calling, streaming

**File**: `apps/backend/llm/providers/openai_provider.py`

**Key Features**:
- GPT-4, GPT-4o, o1 models
- Function calling support
- Streaming support
- Accurate cost tracking

---

### Task 2.4: Anthropic Provider

**Objective**: Implement direct Anthropic API access

**Quality Gate**: Full Anthropic API support, extended thinking

**File**: `apps/backend/llm/providers/anthropic_provider.py`

**Key Features**:
- Claude 3 model family
- Extended thinking support
- Tool use support
- Message batching

---

### Task 2.5: Gemini Provider

**Objective**: Implement Google Gemini API access

**Quality Gate**: Full Gemini support, long context, multimodal

**File**: `apps/backend/llm/providers/gemini_provider.py`

**Key Features**:
- Gemini Pro, Ultra, Flash
- 1M token context support
- Multimodal input
- Google Cloud integration

---

### Task 2.6: Copilot Provider

**Objective**: Implement GitHub Copilot via VS Code LM API

**Quality Gate**: VS Code integration, GitHub auth

**File**: `apps/backend/llm/providers/copilot_provider.py`

**Key Features**:
- VS Code Language Model API
- GitHub authentication
- Copilot-specific models
- IDE integration

---

### Task 2.7: LM Studio Provider

**Objective**: Implement LM Studio for local models

**Quality Gate**: OpenAI-compatible API, local hosting

**File**: `apps/backend/llm/providers/lmstudio_provider.py`

**Key Features**:
- OpenAI-compatible API
- Local model hosting
- Model hot-swap
- Zero cost operation

---

### Task 2.8: Azure Provider

**Objective**: Implement Azure OpenAI for enterprise

**Quality Gate**: Enterprise Azure support, regional endpoints

**File**: `apps/backend/llm/providers/azure_provider.py`

**Key Features**:
- Azure-hosted OpenAI
- Regional deployment support
- Azure AD authentication
- Enterprise compliance

---

## Section 3: LLM Router

### Task 3.1: Implement Router

**Objective**: Create intelligent routing with failover

**Quality Gate**: <5ms overhead, automatic failover, no hardcoded defaults

**File**: `apps/backend/llm/router/router.py`

```python
"""LLM Router - Enterprise-Grade Request Routing.

This module provides intelligent routing of LLM requests to user-configured
providers with automatic failover and health monitoring.

CRITICAL DESIGN PRINCIPLE:
    NO DEFAULT PROVIDER. Users MUST configure at least one provider.
    All providers are treated with equal priority.
    Routing is based SOLELY on user configuration.

Design Patterns:
    - Chain of Responsibility: Failover chain
    - Circuit Breaker: Avoid overloading failed providers
    - Observer: Health status monitoring

Quality Standards:
    - <5ms routing overhead
    - Automatic failover in <500ms
    - Zero downtime during provider switches
"""

from typing import Dict, Optional, List
from datetime import datetime
import asyncio
import logging

from ..abstraction.base_provider import (
    LLMProvider, 
    ProviderHealth, 
    ProviderStatus,
    LLMProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from ..abstraction.message import Message
from ..abstraction.response import LLMResponse
from ..config.agent_llm_config import AgentLLMConfig

logger = logging.getLogger(__name__)

class ProviderNotConfiguredError(Exception):
    """Raised when requested provider is not configured."""
    def __init__(self, provider_id: str, available: List[str]):
        self.provider_id = provider_id
        self.available = available
        super().__init__(
            f"Provider '{provider_id}' not configured. "
            f"Available providers: {available}"
        )

class AllProvidersUnavailableError(Exception):
    """Raised when all providers in fallback chain fail."""
    def __init__(self, primary: str, fallbacks: List[str], errors: List[str]):
        self.primary = primary
        self.fallbacks = fallbacks
        self.errors = errors
        super().__init__(
            f"All providers failed. Primary: {primary}, "
            f"Fallbacks: {fallbacks}. Errors: {errors}"
        )


class LLMRouter:
    """Routes LLM requests to user-configured providers.
    
    ⚠️ CRITICAL DESIGN:
        NO DEFAULT PROVIDER - Users must explicitly configure
        ALL PROVIDERS EQUAL - No favorites or preferences
        FAILOVER CHAIN - Based on user-specified fallback list
    
    World-Class Features:
    - Sub-5ms routing overhead
    - Automatic failover with circuit breaker
    - Real-time health monitoring
    - Request/response logging
    - Cost tracking integration
    
    Example:
        >>> router = LLMRouter()
        >>> router.register_provider(openrouter_provider)
        >>> router.register_provider(ollama_provider)
        >>> 
        >>> config = AgentLLMConfig(
        ...     agent_id="agent-001",
        ...     provider="openrouter",
        ...     model="gpt-4",
        ...     fallback_providers=["ollama"]
        ... )
        >>> 
        >>> response = await router.route(messages, config)
    """
    
    def __init__(self):
        """Initialize router with empty provider registry."""
        self._providers: Dict[str, LLMProvider] = {}
        self._health_cache: Dict[str, ProviderHealth] = {}
        self._circuit_breakers: Dict[str, int] = {}  # Consecutive failures
        self._circuit_breaker_threshold = 5
    
    def register_provider(self, provider: LLMProvider) -> None:
        """Register a configured provider.
        
        Args:
            provider: Configured LLMProvider instance
            
        Raises:
            ValueError: If provider not configured
        """
        if not provider.is_configured:
            raise ValueError(
                f"Provider '{provider.provider_id}' must be configured "
                f"before registration"
            )
        
        self._providers[provider.provider_id] = provider
        self._circuit_breakers[provider.provider_id] = 0
        logger.info(
            f"Registered provider: {provider.provider_id} ({provider.name})"
        )
    
    def unregister_provider(self, provider_id: str) -> bool:
        """Remove provider from registry.
        
        Args:
            provider_id: ID of provider to remove
            
        Returns:
            True if removed, False if not found
        """
        if provider_id in self._providers:
            del self._providers[provider_id]
            self._circuit_breakers.pop(provider_id, None)
            logger.info(f"Unregistered provider: {provider_id}")
            return True
        return False
    
    def get_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """Get provider by ID."""
        return self._providers.get(provider_id)
    
    def list_providers(self) -> List[str]:
        """List all registered provider IDs."""
        return list(self._providers.keys())
    
    def is_circuit_open(self, provider_id: str) -> bool:
        """Check if circuit breaker is open (too many failures)."""
        return self._circuit_breakers.get(provider_id, 0) >= self._circuit_breaker_threshold
    
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
            **kwargs: Additional parameters for provider
            
        Returns:
            LLMResponse from successful provider
            
        Raises:
            ProviderNotConfiguredError: If primary provider not registered
            AllProvidersUnavailableError: If all providers fail
        """
        # Validate primary provider exists
        if config.provider not in self._providers:
            raise ProviderNotConfiguredError(
                config.provider, 
                self.list_providers()
            )
        
        # Build provider chain: primary + fallbacks
        provider_chain = [config.provider] + (config.fallback_providers or [])
        errors: List[str] = []
        
        for provider_id in provider_chain:
            provider = self._providers.get(provider_id)
            if not provider:
                logger.warning(f"Fallback provider not found: {provider_id}")
                continue
            
            # Check circuit breaker
            if self.is_circuit_open(provider_id):
                logger.warning(f"Circuit open for {provider_id}, skipping")
                errors.append(f"{provider_id}: circuit breaker open")
                continue
            
            try:
                logger.debug(f"Attempting provider: {provider_id}")
                response = await provider.complete(
                    messages,
                    model=config.model if provider_id == config.provider else None,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    **kwargs
                )
                
                # Success - reset circuit breaker
                self._circuit_breakers[provider_id] = 0
                
                logger.info(
                    f"Request routed to {provider_id}/{response.model}, "
                    f"tokens: {response.usage.total_tokens}, "
                    f"latency: {response.latency_ms}ms"
                )
                return response
                
            except RateLimitError as e:
                logger.warning(f"Rate limited by {provider_id}: {e}")
                errors.append(f"{provider_id}: rate limited")
                # Don't increment circuit breaker for rate limits
                continue
                
            except LLMProviderError as e:
                logger.error(f"Provider error from {provider_id}: {e}")
                errors.append(f"{provider_id}: {str(e)}")
                self._circuit_breakers[provider_id] += 1
                continue
                
            except Exception as e:
                logger.exception(f"Unexpected error from {provider_id}")
                errors.append(f"{provider_id}: {str(e)}")
                self._circuit_breakers[provider_id] += 1
                continue
        
        # All providers failed
        raise AllProvidersUnavailableError(
            config.provider,
            config.fallback_providers or [],
            errors
        )
    
    async def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Check health of all registered providers concurrently.
        
        Returns:
            Dictionary of provider_id -> ProviderHealth
        """
        tasks = {
            provider_id: provider.health_check()
            for provider_id, provider in self._providers.items()
        }
        
        results = {}
        for provider_id, task in tasks.items():
            try:
                results[provider_id] = await task
                self._health_cache[provider_id] = results[provider_id]
            except Exception as e:
                results[provider_id] = ProviderHealth(
                    status=ProviderStatus.UNAVAILABLE,
                    error=str(e),
                    last_checked=datetime.utcnow().isoformat()
                )
        
        return results
    
    def get_cached_health(self, provider_id: str) -> Optional[ProviderHealth]:
        """Get last known health status."""
        return self._health_cache.get(provider_id)
    
    def reset_circuit_breaker(self, provider_id: str) -> None:
        """Manually reset circuit breaker for provider."""
        self._circuit_breakers[provider_id] = 0
        logger.info(f"Circuit breaker reset for {provider_id}")
```

**Validation Checklist**:
- [ ] No default provider anywhere
- [ ] All providers treated equally
- [ ] Failover chain works
- [ ] Circuit breaker functions
- [ ] <5ms routing overhead
- [ ] Health check works

**Expected Outcome**: World-class routing that ensures reliability without vendor lock-in.

---

### Task 3.2: Implement Health Monitor

**Objective**: Continuous provider health monitoring

**File**: `apps/backend/llm/router/health.py`

---

### Task 3.3: Implement Failover Logic

**Objective**: Sophisticated failover with circuit breaker

**File**: `apps/backend/llm/router/failover.py`

---

## Section 4: Agent LLM Configuration

### Task 4.1: Create Config Manager

**Objective**: Manage per-agent LLM configurations

**Quality Gate**: Persistent storage, validation, hot-reload

**File**: `apps/backend/llm/config/agent_llm_config.py`

```python
"""Per-Agent LLM Configuration Management - Enterprise-Grade.

This module manages the configuration that allows each agent
to use a DIFFERENT LLM provider and model independently.

CRITICAL DESIGN:
    - Each agent can have completely different LLM settings
    - No global defaults - all configuration explicit
    - Configurations persist across restarts
    - Hot-reload without restart

Quality Standards:
    - Type-safe configuration
    - Validation on load/save
    - Encryption for sensitive data
    - Audit logging
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentLLMConfig:
    """Configuration for an agent's LLM provider.
    
    CRITICAL: Each agent can use a COMPLETELY DIFFERENT provider/model.
    
    Attributes:
        agent_id: Unique agent identifier
        provider: Chosen provider (e.g., "openrouter", "ollama")
        model: Chosen model (e.g., "gpt-4", "llama-3")
        fallback_providers: Ordered backup provider list
        max_tokens: Maximum tokens for responses
        temperature: Creativity setting (0.0-2.0)
        timeout_seconds: Request timeout
        retry_attempts: Number of retries on failure
        cost_budget_daily: Optional daily cost limit in USD
        cost_budget_monthly: Optional monthly cost limit in USD
        enabled: Whether agent should use LLM
        created_at: Configuration creation time
        updated_at: Last modification time
        
    Example:
        >>> config = AgentLLMConfig(
        ...     agent_id="code-review-agent-001",
        ...     provider="openrouter",
        ...     model="anthropic/claude-3-opus",
        ...     fallback_providers=["ollama", "openai"],
        ...     max_tokens=8192,
        ...     temperature=0.3  # Low for code review
        ... )
    """
    agent_id: str
    provider: str
    model: str
    fallback_providers: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 120
    retry_attempts: int = 3
    cost_budget_daily: Optional[float] = None
    cost_budget_monthly: Optional[float] = None
    enabled: bool = True
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        
        # Validation
        if not self.agent_id:
            raise ValueError("agent_id is required")
        if not self.provider:
            raise ValueError("provider is required")
        if not self.model:
            raise ValueError("model is required")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentLLMConfig':
        """Create from dictionary."""
        return cls(**data)


class AgentLLMConfigManager:
    """Manages per-agent LLM configurations with persistence.
    
    World-Class Features:
    - File-based persistence with atomic writes
    - In-memory caching for fast access
    - Validation on all operations
    - Hot-reload support
    - Audit logging
    
    Example:
        >>> manager = AgentLLMConfigManager()
        >>> manager.set(config)
        >>> retrieved = manager.get("agent-001")
    """
    
    def __init__(self, config_path: str = "data/agent_llm_configs.json"):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._configs: Dict[str, AgentLLMConfig] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configurations from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for agent_id, config_data in data.items():
                        try:
                            self._configs[agent_id] = AgentLLMConfig.from_dict(config_data)
                        except Exception as e:
                            logger.error(f"Invalid config for {agent_id}: {e}")
                logger.info(f"Loaded {len(self._configs)} agent LLM configs")
            except Exception as e:
                logger.error(f"Failed to load configs: {e}")
    
    def _save(self) -> None:
        """Save configurations to file atomically."""
        data = {
            agent_id: config.to_dict() 
            for agent_id, config in self._configs.items()
        }
        
        # Atomic write via temp file
        temp_path = self.config_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        temp_path.replace(self.config_path)
        
        logger.debug(f"Saved {len(data)} agent LLM configs")
    
    def get(self, agent_id: str) -> Optional[AgentLLMConfig]:
        """Get configuration for agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Configuration if exists, None otherwise
        """
        return self._configs.get(agent_id)
    
    def set(self, config: AgentLLMConfig) -> None:
        """Set configuration for agent.
        
        Args:
            config: Agent LLM configuration
        """
        config.updated_at = datetime.utcnow().isoformat()
        self._configs[config.agent_id] = config
        self._save()
        logger.info(
            f"Set LLM config for {config.agent_id}: "
            f"{config.provider}/{config.model}"
        )
    
    def delete(self, agent_id: str) -> bool:
        """Delete configuration for agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if deleted, False if not found
        """
        if agent_id in self._configs:
            del self._configs[agent_id]
            self._save()
            logger.info(f"Deleted LLM config for {agent_id}")
            return True
        return False
    
    def list_all(self) -> List[AgentLLMConfig]:
        """List all configurations."""
        return list(self._configs.values())
    
    def reload(self) -> int:
        """Reload configurations from file.
        
        Returns:
            Number of configurations loaded
        """
        self._configs.clear()
        self._load()
        return len(self._configs)
    
    def get_by_provider(self, provider: str) -> List[AgentLLMConfig]:
        """Get all configs using a specific provider."""
        return [c for c in self._configs.values() if c.provider == provider]
```

**Validation Checklist**:
- [ ] Persistence works correctly
- [ ] Validation catches invalid configs
- [ ] Atomic writes prevent corruption
- [ ] Hot-reload works
- [ ] All operations logged

**Expected Outcome**: Robust configuration management for per-agent LLM settings.

---

## Validation Checklist

| Item | Check | Status |
|------|-------|--------|
| All 8 providers implement LLMProvider interface | Interface compliance | ⬜ |
| Router has no default provider | Code review | ⬜ |
| All providers treated equally | Code review | ⬜ |
| Per-agent configuration works | Integration test | ⬜ |
| Failover chain functional | Failover test | ⬜ |
| Circuit breaker protects failed providers | Stress test | ⬜ |
| Health monitoring operational | Health check test | ⬜ |
| Response normalization correct | Response format test | ⬜ |
| Cost tracking accurate | Cost calculation test | ⬜ |
| Test coverage >95% | Coverage report | ⬜ |
| Type hints validate (mypy) | mypy execution | ⬜ |
| Production-ready error handling | Code review | ⬜ |
| World-class patterns used | Architecture review | ⬜ |

---

## Dependencies

**Requires**: Phase 1 (Foundation - AgentLLMConfig used)

**Enables**: Phase 3 (Auth - credentials link to providers), Phase 7 (Enterprise Agents - use router)

---

## ADR References

- ADR-005: LLM-Agnostic Architecture (REWRITTEN)
- ADR-013: Per-Agent LLM Configuration

---

*Phase 2 Specification v2.0.0 - Enhanced with World-Class Outcome Expectations*
