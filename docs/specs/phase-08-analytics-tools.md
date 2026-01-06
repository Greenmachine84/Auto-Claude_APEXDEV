# Phase 8: Analytics & Tools

> **Version**: 2.0.0 | **Duration**: Week 15-16 | **Priority**: 🟡 MEDIUM
>
> **Status**: 📋 Specification Ready
>
> **LLM-Agnostic**: ✅ Usage/cost tracking for all 8 providers

---

## Quality Standards

| Standard | Description | Verification |
|----------|-------------|--------------|
| **World-Class** | Comprehensive observability | Dashboard review |
| **Enterprise-Grade** | Real-time analytics at scale | Load testing |
| **Fully Production Ready** | Accurate cost attribution | Financial audit |
| **Clean and Concise Code** | Modular metrics architecture | Code review |
| **Beyond PhD Level Expertise** | Advanced analytics patterns | Expert assessment |

---

## Outcome Expectations

### Business Objectives

| Objective | Success Metric | World-Class Standard |
|-----------|----------------|----------------------|
| Cost visibility | Per-provider breakdown | Real-time cost tracking |
| Usage insights | Detailed analytics | Business intelligence ready |
| Tool extensibility | Plugin architecture | Enterprise customization |
| Performance monitoring | Real-time metrics | SLA compliance |

### Technical Outcomes

| Outcome | Measurement | Target | World-Class Standard |
|---------|-------------|--------|----------------------|
| Metrics latency | Event to dashboard | <5s | Real-time visibility |
| Cost accuracy | Calculation error | <0.1% | Financial-grade precision |
| Tool execution | P99 latency | <100ms | Instant tool response |
| Data retention | Metrics history | 90 days | Full audit trail |
| Dashboard load | Page render | <2s | Responsive UI |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| Usage metrics collected | Events tracked | ✅ | 100% event capture |
| Cost tracking works | Per-provider/model | ✅ | All 8 providers tracked |
| Dashboard API functional | Metrics endpoints | ✅ | Real-time updates |
| Tool registry works | CRUD operations | ✅ | Hot-reload support |
| Tool execution works | Agent tool calls | ✅ | <100ms execution |
| Provider comparison | Side-by-side metrics | ✅ | Cost optimization insights |

---

## Acceptance Tests

| Test ID | Test Case | Pass Criteria | Verification Method |
|---------|-----------|---------------|---------------------|
| AT-8.1 | Record 100K events | All persisted correctly | Load test |
| AT-8.2 | Cost tracking accuracy | Within 0.1% of actual | Financial audit |
| AT-8.3 | Dashboard real-time update | <5s event-to-display | Integration test |
| AT-8.4 | Track usage for each provider | All 8 providers recorded | Unit test |
| AT-8.5 | Tool registry CRUD | All operations work | Unit test |
| AT-8.6 | Tool execution sandbox | No host access | Security test |
| AT-8.7 | Provider cost comparison | Accurate breakdown | Unit test |
| AT-8.8 | Usage report export | CSV/JSON export works | Integration test |
| AT-8.9 | Rate limit by provider | Per-provider limits work | Integration test |
| AT-8.10 | Custom tool registration | User tools loadable | End-to-end test |

---

## Performance Metrics

| Metric | Target | Measurement Method | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Event ingestion | >10K events/s | Load test | <5K events/s |
| Cost calculation | <1ms | Benchmark | >5ms |
| Dashboard API | <100ms P99 | Prometheus | >500ms |
| Tool execution | <100ms P99 | Prometheus | >500ms |
| Aggregation query | <500ms | Benchmark | >2s |
| Export generation | <10s for 1M rows | Benchmark | >30s |

---

## Risk Mitigations

| Risk | Impact | Mitigation | Verification |
|------|--------|------------|--------------|
| Data loss | Missing metrics | Write-ahead log | Recovery test |
| Cost calculation error | Billing disputes | Audit logging | Financial review |
| Tool execution escape | Security breach | Sandboxed execution | Pen test |
| Dashboard overload | Poor UX | Caching + pagination | Load test |
| Provider API changes | Wrong pricing | Configurable pricing | Unit tests |

---

## LLM-Agnostic Analytics

### Multi-Provider Usage Tracking

```python
"""
Usage and cost tracking for ALL 8 LLM providers.
Each provider has its own pricing model.
NO DEFAULT - all providers tracked equally.
"""

# Provider pricing per 1M tokens (input, output)
PROVIDER_PRICING = {
    "copilot": {
        "default": (0.0, 0.0),  # Included in subscription
    },
    "openrouter": {
        "anthropic/claude-3-opus": (15.0, 75.0),
        "openai/gpt-4": (30.0, 60.0),
        "meta-llama/llama-3-70b": (0.9, 0.9),
        "default": (1.0, 2.0),
    },
    "ollama": {
        "default": (0.0, 0.0),  # Local, no API cost
    },
    "lmstudio": {
        "default": (0.0, 0.0),  # Local, no API cost
    },
    "gemini": {
        "gemini-1.5-pro": (3.5, 10.5),
        "gemini-1.5-flash": (0.35, 1.05),
        "gemini-1.0-pro": (0.5, 1.5),
    },
    "openai": {
        "gpt-4o": (5.0, 15.0),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.0, 30.0),
        "gpt-3.5-turbo": (0.5, 1.5),
    },
    "anthropic": {
        "claude-sonnet-4-20250514": (3.0, 15.0),
        "claude-3-opus": (15.0, 75.0),
        "claude-3-haiku": (0.25, 1.25),
    },
    "azure": {
        "gpt-4o": (5.0, 15.0),
        "gpt-4": (30.0, 60.0),
        "default": (5.0, 15.0),
    },
}


@dataclass
class ProviderUsageMetrics:
    """Usage metrics for a specific provider."""
    provider: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    models_used: Dict[str, int] = field(default_factory=dict)


class MultiProviderCostTracker:
    """
    Cost tracker for all 8 LLM providers.
    
    Tracks usage and calculates costs for:
    - copilot, openrouter, ollama, lmstudio
    - gemini, openai, anthropic, azure
    """
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost for any provider.
        
        Args:
            provider: One of 8 supported providers
            model: Provider-specific model name
        """
        if provider not in PROVIDER_PRICING:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: {', '.join(PROVIDER_PRICING.keys())}"
            )
        
        pricing = PROVIDER_PRICING[provider]
        
        # Find model-specific or default pricing
        model_pricing = pricing.get(model) or pricing.get("default", (1.0, 2.0))
        
        input_cost = (prompt_tokens / 1_000_000) * model_pricing[0]
        output_cost = (completion_tokens / 1_000_000) * model_pricing[1]
        
        return round(input_cost + output_cost, 6)
    
    async def get_provider_comparison(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, ProviderUsageMetrics]:
        """
        Get side-by-side comparison of all providers.
        
        Returns metrics for each of 8 providers used.
        """
        metrics = {}
        
        for provider in PROVIDER_PRICING.keys():
            usage = await self._get_provider_usage(user_id, provider, days)
            if usage.total_requests > 0:
                metrics[provider] = usage
        
        return metrics
```

### Provider Cost Dashboard Data

```python
@dataclass
class DashboardData:
    """Dashboard data structure for multi-provider analytics."""
    period_start: str
    period_end: str
    
    # Overall metrics
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # Per-provider breakdown (all 8)
    by_provider: Dict[str, ProviderUsageMetrics] = field(default_factory=dict)
    
    # Per-agent breakdown
    by_agent: Dict[str, Dict] = field(default_factory=dict)
    
    # Time series for charts
    hourly_requests: List[Dict] = field(default_factory=list)
    hourly_cost: List[Dict] = field(default_factory=list)
    
    # Cost optimization recommendations
    recommendations: List[str] = field(default_factory=list)
```

---

## Deliverables

| File | Purpose | LOC Estimate |
|------|---------|--------------|
| `apps/backend/analytics/metrics/collector.py` | Event collection | 250 |
| `apps/backend/analytics/metrics/aggregator.py` | Metric aggregation | 200 |
| `apps/backend/analytics/cost/cost_tracker.py` | Multi-provider costs | 350 |
| `apps/backend/analytics/cost/pricing.py` | Provider pricing | 150 |
| `apps/backend/analytics/dashboard/api.py` | Dashboard endpoints | 300 |
| `apps/backend/tools/registry/tool_registry.py` | Tool management | 200 |
| `apps/backend/tools/executor/tool_executor.py` | Sandboxed execution | 300 |
| `apps/backend/tools/builtin/*.py` | Built-in tools | 400 |
| `tests/test_analytics_*.py` | Analytics tests | 600 |

---

## Section 1: Analytics Architecture

### Task 1.1: Directory Structure

```
apps/backend/analytics/
├── __init__.py
├── models.py
├── metrics/
│   ├── __init__.py
│   ├── collector.py
│   └── aggregator.py
├── cost/
│   ├── __init__.py
│   ├── cost_tracker.py
│   └── pricing.py
└── dashboard/
    ├── __init__.py
    └── api.py

apps/backend/tools/
├── __init__.py
├── models.py
├── registry/
│   ├── __init__.py
│   └── tool_registry.py
├── executor/
│   ├── __init__.py
│   └── tool_executor.py
└── builtin/
    ├── __init__.py
    ├── file_tools.py
    ├── web_tools.py
    └── git_tools.py
```

### Task 1.2: Analytics Models

**File**: `apps/backend/analytics/models.py`

```python
"""
Analytics models for multi-provider tracking.

World-Class Standards:
- Comprehensive metric types
- Provider-aware event tracking
- Cost attribution support
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MetricType(Enum):
    """Metric types for different measurement patterns."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventType(Enum):
    """Trackable event types."""
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    TOOL_CALLED = "tool_called"
    MEMORY_ACCESS = "memory_access"
    USER_LOGIN = "user_login"
    PROVIDER_SWITCH = "provider_switch"


@dataclass
class MetricEvent:
    """
    Single metric event with provider tracking.
    
    Tracks which of 8 providers was used.
    """
    id: str
    event_type: EventType
    timestamp: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    provider: Optional[str] = None  # One of 8 LLM providers
    model: Optional[str] = None
    value: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostRecord:
    """Cost record for billing with provider attribution."""
    id: str
    user_id: str
    provider: str  # copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: str
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
```

---

## Section 2: Multi-Provider Cost Tracking

### Task 2.1: Cost Tracker

**File**: `apps/backend/analytics/cost/cost_tracker.py`

```python
"""
Cost tracking for all 8 LLM providers.

World-Class Standards:
- Financial-grade accuracy
- Real-time cost calculation
- Provider comparison support
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import uuid
from ..models import CostRecord
from .pricing import PROVIDER_PRICING


class CostTracker:
    """
    Tracks LLM costs across all 8 providers.
    
    Supports:
    - copilot (subscription-based)
    - openrouter (pay-per-use)
    - ollama (free, local)
    - lmstudio (free, local)
    - gemini (Google pricing)
    - openai (OpenAI pricing)
    - anthropic (Anthropic pricing)
    - azure (Azure pricing)
    """
    
    SUPPORTED_PROVIDERS = [
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    ]
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost for token usage on any provider.
        
        Local providers (ollama, lmstudio) return 0.0.
        Subscription providers (copilot) return 0.0.
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )
        
        pricing = PROVIDER_PRICING.get(provider, {})
        model_pricing = pricing.get(model) or pricing.get("default", (0.0, 0.0))
        
        input_cost = (prompt_tokens / 1_000_000) * model_pricing[0]
        output_cost = (completion_tokens / 1_000_000) * model_pricing[1]
        
        return round(input_cost + output_cost, 6)
    
    async def get_provider_breakdown(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Dict]:
        """
        Get cost breakdown by provider.
        
        Returns stats for each of 8 providers that was used.
        """
        breakdown = {}
        
        for provider in self.SUPPORTED_PROVIDERS:
            stats = await self._get_provider_stats(user_id, provider, days)
            if stats["total_requests"] > 0:
                breakdown[provider] = stats
        
        return breakdown
```

---

## Section 3: Dashboard API

### Task 3.1: Dashboard Endpoints

**File**: `apps/backend/analytics/dashboard/api.py`

```python
"""
Dashboard API for analytics visualization.

World-Class Standards:
- Real-time data access
- Multi-provider comparison
- Export capabilities
"""
from fastapi import APIRouter, Depends
from typing import Optional
from datetime import datetime, timedelta
from ..cost.cost_tracker import CostTracker
from ..metrics.aggregator import MetricsAggregator


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(
    days: int = 30,
    user_id: str = Depends(get_current_user)
):
    """
    Get dashboard data with multi-provider breakdown.
    
    Returns metrics for all 8 providers used.
    """
    cost_tracker = CostTracker()
    aggregator = MetricsAggregator()
    
    return {
        "period": {
            "start": (datetime.utcnow() - timedelta(days=days)).isoformat(),
            "end": datetime.utcnow().isoformat(),
        },
        "overview": await aggregator.get_overview(user_id, days),
        "by_provider": await cost_tracker.get_provider_breakdown(user_id, days),
        "by_agent": await aggregator.get_agent_breakdown(user_id, days),
        "time_series": await aggregator.get_time_series(user_id, days),
        "recommendations": await get_cost_recommendations(user_id),
    }


@router.get("/provider-comparison")
async def compare_providers(
    user_id: str = Depends(get_current_user)
):
    """
    Compare all 8 providers side-by-side.
    
    Useful for cost optimization decisions.
    """
    cost_tracker = CostTracker()
    return await cost_tracker.get_provider_comparison(user_id)
```

---

## Section 4: Tool Registry

### Task 4.1: Tool Registry

**File**: `apps/backend/tools/registry/tool_registry.py`

```python
"""
Tool registry for agent tools.

World-Class Standards:
- Hot-reload support
- Sandboxed execution
- Type-safe definitions
"""
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    """Tool definition with schema."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    category: str = "general"
    requires_auth: bool = False
    timeout_seconds: int = 30


class ToolRegistry:
    """
    Registry for agent-callable tools.
    
    Supports built-in and custom tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._load_builtin_tools()
    
    def register(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get tool by name."""
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List available tools."""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
```

---

## Validation Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| LLM-Agnostic System | ✅ | Cost tracking for all 8 providers |
| No Default Provider | ✅ | Each provider tracked separately |
| 8 Equal LLM Providers | ✅ | PROVIDER_PRICING dictionary |
| Per-Agent LLM Assignment | ✅ | by_agent breakdown |
| World-Class Standards | ✅ | Quality Standards table |
| Enterprise-Grade | ✅ | Real-time at scale |
| Production Ready | ✅ | Financial-grade accuracy |
| Clean Code | ✅ | Modular architecture |
| Acceptance Tests | ✅ | AT-8.1 through AT-8.10 |
| Performance Metrics | ✅ | <100ms P99 targets |

---

## Integration Points

| Phase | Integration | Data Flow |
|-------|-------------|-----------|
| Phase 2 | LLM Router | Usage events |
| Phase 4 | Orchestration | Task metrics |
| Phase 5 | Memory | Access tracking |
| Phase 7 | Agents | Agent metrics |
