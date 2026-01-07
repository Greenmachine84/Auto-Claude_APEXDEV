"""
Analytics Data Models - Phase 8 Implementation.

Comprehensive data models for multi-provider analytics tracking.

World-Class Standards:
- Type-safe with full annotations
- Dataclass-based for immutability
- Provider-aware event tracking
- Cost attribution support

LLM-Agnostic: Supports all 8 providers equally:
- copilot, openrouter, ollama, lmstudio
- gemini, openai, anthropic, azure
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


# =============================================================================
# SUPPORTED PROVIDERS (8 total, equal treatment)
# =============================================================================

SUPPORTED_PROVIDERS = [
    "copilot",      # GitHub Copilot (subscription-based)
    "openrouter",   # OpenRouter (pay-per-use, multi-model)
    "ollama",       # Ollama (local, free)
    "lmstudio",     # LM Studio (local, free)
    "gemini",       # Google Gemini (pay-per-use)
    "openai",       # OpenAI (pay-per-use)
    "anthropic",    # Anthropic Claude (pay-per-use)
    "azure",        # Azure OpenAI (pay-per-use)
]


# =============================================================================
# ENUMS
# =============================================================================

class MetricType(Enum):
    """
    Metric types for different measurement patterns.
    
    Follows Prometheus conventions:
    - COUNTER: Monotonically increasing value
    - GAUGE: Value that can go up or down
    - HISTOGRAM: Distribution of values
    - TIMER: Duration measurements
    """
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventType(Enum):
    """
    Trackable event types for analytics.
    
    Covers all major system activities with provider attribution.
    """
    # Agent lifecycle
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    
    # Task lifecycle
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # LLM interactions (provider-tracked)
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"
    LLM_RETRY = "llm_retry"
    
    # Tool usage
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    
    # Memory operations
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    MEMORY_SEARCH = "memory_search"
    
    # User activity
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    
    # Provider management
    PROVIDER_SWITCH = "provider_switch"
    PROVIDER_ERROR = "provider_error"
    
    # Budget events
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"


class BudgetStatusType(Enum):
    """Budget status levels."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class MetricEvent:
    """
    Single metric event with provider tracking.
    
    Immutable dataclass for event capture.
    Tracks which of 8 providers was used for LLM events.
    
    Attributes:
        id: Unique event identifier
        event_type: Type of event from EventType enum
        timestamp: ISO format timestamp
        user_id: Optional user identifier
        agent_id: Optional agent identifier
        provider: One of 8 LLM providers (for LLM events)
        model: Provider-specific model name
        value: Numeric metric value (default 1.0)
        metadata: Additional event context
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
    
    def __post_init__(self) -> None:
        """Validate provider if specified."""
        if self.provider is not None and self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
    
    @classmethod
    def create(
        cls,
        event_type: EventType,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        value: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "MetricEvent":
        """Factory method for creating events with auto-generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            user_id=user_id,
            agent_id=agent_id,
            provider=provider,
            model=model,
            value=value,
            metadata=metadata or {},
        )


@dataclass
class CostRecord:
    """
    Cost record for billing with provider attribution.
    
    Tracks token usage and cost for each LLM request.
    All 8 providers are supported with their pricing models.
    
    Attributes:
        id: Unique record identifier
        user_id: User who incurred the cost
        provider: LLM provider (copilot, openrouter, ollama, etc.)
        model: Provider-specific model name
        prompt_tokens: Input tokens used
        completion_tokens: Output tokens generated
        cost_usd: Calculated cost in USD
        timestamp: ISO format timestamp
        agent_id: Optional agent attribution
        task_id: Optional task attribution
    """
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
    
    def __post_init__(self) -> None:
        """Validate provider."""
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.prompt_tokens + self.completion_tokens
    
    @classmethod
    def create(
        cls,
        user_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> "CostRecord":
        """Factory method for creating cost records."""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost_usd,
            timestamp=datetime.utcnow().isoformat() + "Z",
            agent_id=agent_id,
            task_id=task_id,
        )


@dataclass
class ProviderUsageMetrics:
    """
    Aggregated usage metrics for a specific provider.
    
    Used for per-provider dashboard breakdown.
    All 8 providers are tracked equally.
    """
    provider: str
    total_requests: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    models_used: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate provider."""
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )


@dataclass
class TimeSeriesPoint:
    """
    Single point in a time series.
    
    Used for dashboard charts and trend analysis.
    """
    timestamp: str
    value: float
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetStatus:
    """
    Budget status for a user/provider combination.
    
    Tracks spending against configured limits.
    """
    user_id: str
    provider: str
    monthly_limit: float
    current_spend: float
    remaining: float
    status: BudgetStatusType
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    
    @property
    def usage_percentage(self) -> float:
        """Percentage of budget used."""
        if self.monthly_limit <= 0:
            return 0.0
        return (self.current_spend / self.monthly_limit) * 100
    
    @classmethod
    def calculate(
        cls,
        user_id: str,
        provider: str,
        monthly_limit: float,
        current_spend: float,
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95,
    ) -> "BudgetStatus":
        """Calculate budget status from current spend."""
        remaining = max(0.0, monthly_limit - current_spend)
        
        if monthly_limit <= 0:
            status = BudgetStatusType.OK
        elif current_spend > monthly_limit:
            status = BudgetStatusType.EXCEEDED
        elif current_spend >= monthly_limit * critical_threshold:
            status = BudgetStatusType.CRITICAL
        elif current_spend >= monthly_limit * warning_threshold:
            status = BudgetStatusType.WARNING
        else:
            status = BudgetStatusType.OK
        
        return cls(
            user_id=user_id,
            provider=provider,
            monthly_limit=monthly_limit,
            current_spend=current_spend,
            remaining=remaining,
            status=status,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
        )


@dataclass
class DashboardData:
    """
    Dashboard data structure for multi-provider analytics.
    
    Comprehensive view of usage across all 8 providers.
    Designed for real-time dashboard updates.
    """
    period_start: str
    period_end: str
    
    # Overall metrics
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # Per-provider breakdown (all 8 providers tracked)
    by_provider: Dict[str, ProviderUsageMetrics] = field(default_factory=dict)
    
    # Per-agent breakdown
    by_agent: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Time series for charts
    hourly_requests: List[TimeSeriesPoint] = field(default_factory=list)
    hourly_cost: List[TimeSeriesPoint] = field(default_factory=list)
    daily_tokens: List[TimeSeriesPoint] = field(default_factory=list)
    
    # Cost optimization recommendations
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def active_providers(self) -> List[str]:
        """List of providers with recorded usage."""
        return [p for p, m in self.by_provider.items() if m.total_requests > 0]
    
    @property
    def provider_count(self) -> int:
        """Number of providers with usage."""
        return len(self.active_providers)


@dataclass
class AgentMetrics:
    """
    Aggregated metrics for a specific agent.
    
    Tracks performance and cost per agent.
    """
    agent_id: str
    agent_type: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    avg_task_duration_ms: float = 0.0
    providers_used: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Task success rate as percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100


@dataclass
class MetricsSummary:
    """
    High-level metrics summary for quick dashboard view.
    """
    total_requests: int
    total_tokens: int
    total_cost: float
    active_agents: int
    active_providers: int
    avg_latency_ms: float
    error_rate: float
    period_start: str
    period_end: str
