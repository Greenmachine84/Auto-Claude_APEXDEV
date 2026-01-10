"""
Governance Data Models - Phase 9 Implementation.

Enterprise governance models for policy management, approval workflows,
rate limiting, and compliance.

World-Class Standards:
- Type-safe with full annotations
- Dataclass-based for immutability
- Provider-aware governance
- Comprehensive audit support

LLM-Agnostic: Supports all 8 providers equally:
- copilot, openrouter, ollama, lmstudio
- gemini, openai, anthropic, azure
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# SUPPORTED PROVIDERS (8 total, equal treatment)
# =============================================================================

SUPPORTED_PROVIDERS = [
    "copilot",  # GitHub Copilot (subscription-based)
    "openrouter",  # OpenRouter (pay-per-use, multi-model)
    "ollama",  # Ollama (local, free)
    "lmstudio",  # LM Studio (local, free)
    "gemini",  # Google Gemini (pay-per-use)
    "openai",  # OpenAI (pay-per-use)
    "anthropic",  # Anthropic Claude (pay-per-use)
    "azure",  # Azure OpenAI (pay-per-use)
]


# =============================================================================
# ENUMS
# =============================================================================


class PolicyAction(Enum):
    """
    Actions a policy can take.

    - ALLOW: Request proceeds
    - DENY: Request blocked
    - REQUIRE_APPROVAL: Needs approval workflow
    - LOG: Allow but log for audit
    - WARN: Allow with warning
    """

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG = "log"
    WARN = "warn"


class ApprovalStatus(Enum):
    """
    Status of an approval request.

    Lifecycle: PENDING -> APPROVED/REJECTED/EXPIRED/CANCELLED
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RuleOperator(Enum):
    """
    Operators for rule conditions.

    Supports numeric, string, and collection operations.
    """

    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GE = "ge"  # Greater than or equal
    LT = "lt"  # Less than
    LE = "le"  # Less than or equal
    IN = "in"  # In collection
    NOT_IN = "not_in"  # Not in collection
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"  # Regex match


class LimitType(Enum):
    """
    Types of rate/quota limits.
    """

    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    TOKENS_PER_MINUTE = "tokens_per_minute"
    TOKENS_PER_DAY = "tokens_per_day"
    COST_PER_DAY = "cost_per_day"
    COST_PER_MONTH = "cost_per_month"


class ComplianceEventType(Enum):
    """
    Types of compliance events for audit trail.
    """

    POLICY_EVALUATED = "policy_evaluated"
    POLICY_DENIED = "policy_denied"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    RATE_LIMIT_HIT = "rate_limit_hit"
    QUOTA_EXCEEDED = "quota_exceeded"
    QUOTA_WARNING = "quota_warning"
    CONFIG_CHANGED = "config_changed"
    ACCESS_DENIED = "access_denied"


# =============================================================================
# POLICY MODELS
# =============================================================================


@dataclass
class PolicyRule:
    """
    Single policy rule with provider awareness.

    Attributes:
        id: Unique rule identifier
        name: Human-readable rule name
        field: Context field to evaluate
        operator: Comparison operator
        value: Value to compare against
        action: Action when rule matches
        priority: Higher priority rules evaluated first
        provider: Optional provider-specific rule
    """

    id: str
    name: str
    description: str = ""
    field: str = ""
    operator: RuleOperator = RuleOperator.EQ
    value: Any = None
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0
    enabled: bool = True
    provider: str | None = None  # Apply only to specific provider

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.provider and self.provider not in SUPPORTED_PROVIDERS:
            logger.warning(f"Rule {self.id}: Unknown provider '{self.provider}'")


@dataclass
class Policy:
    """
    Collection of rules for governance.

    Policies contain ordered rules evaluated by priority.
    First matching rule determines the action.
    """

    id: str
    name: str
    description: str = ""
    rules: list[PolicyRule] = field(default_factory=list)
    default_action: PolicyAction = PolicyAction.ALLOW
    enabled: bool = True
    applies_to: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class PolicyEvaluation:
    """
    Result of policy evaluation.

    Contains the decision and reasoning for audit trail.
    """

    policy_id: str
    action: PolicyAction
    reason: str
    matched_rule: str | None = None
    evaluation_time_ms: float = 0.0
    provider: str | None = None
    context_snapshot: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# APPROVAL MODELS
# =============================================================================


@dataclass
class ApprovalRequest:
    """
    Request requiring approval with provider context.

    Tracks multi-step approval workflows with audit trail.
    """

    id: str
    request_type: str
    requester_id: str
    description: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    provider: str | None = None  # Track provider for approval
    model: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    approvers: list[str] = field(default_factory=list)
    approved_by: str | None = None
    rejected_by: str | None = None
    rejection_reason: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    decided_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ApprovalStep:
    """
    Single step in a multi-step approval workflow.
    """

    step_id: str
    approver_id: str
    order: int
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_at: datetime | None = None
    comments: str = ""


@dataclass
class WorkflowDefinition:
    """
    Definition of an approval workflow.
    """

    id: str
    name: str
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    require_all: bool = True  # All approvers required vs any one
    timeout_hours: int = 24
    escalation_path: list[str] = field(default_factory=list)
    enabled: bool = True


# =============================================================================
# RATE LIMIT MODELS
# =============================================================================


@dataclass
class RateLimit:
    """
    Rate limit configuration.
    """

    limit_type: LimitType
    limit_value: int
    window_seconds: int
    provider: str | None = None  # Provider-specific limit
    user_id: str | None = None  # User-specific limit

    @property
    def key(self) -> str:
        """Generate storage key for this limit."""
        parts = [self.limit_type.value]
        if self.provider:
            parts.append(f"provider:{self.provider}")
        if self.user_id:
            parts.append(f"user:{self.user_id}")
        return ":".join(parts)


@dataclass
class RateLimitResult:
    """
    Result of rate limit check.
    """

    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime
    retry_after_seconds: int | None = None


# =============================================================================
# QUOTA MODELS
# =============================================================================


@dataclass
class Quota:
    """
    Quota configuration.
    """

    quota_type: LimitType
    limit_value: float
    period_days: int = 30  # Monthly by default
    provider: str | None = None
    user_id: str | None = None

    @property
    def key(self) -> str:
        """Generate storage key for this quota."""
        parts = [self.quota_type.value]
        if self.provider:
            parts.append(f"provider:{self.provider}")
        if self.user_id:
            parts.append(f"user:{self.user_id}")
        return ":".join(parts)


@dataclass
class QuotaUsage:
    """
    Current quota usage status.
    """

    quota_key: str
    current_usage: float
    limit: float
    remaining: float
    usage_percent: float
    period_start: datetime
    period_end: datetime
    provider: str | None = None


# =============================================================================
# COMPLIANCE MODELS
# =============================================================================


@dataclass
class ComplianceEvent:
    """
    Compliance event for audit trail.

    Immutable record of governance actions.
    """

    id: str
    event_type: ComplianceEventType
    timestamp: datetime
    user_id: str | None = None
    agent_id: str | None = None
    provider: str | None = None
    resource: str = ""
    action: str = ""
    result: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    session_id: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class AuditRecord:
    """
    Full audit record with integrity verification.
    """

    id: str
    event: ComplianceEvent
    checksum: str = ""
    previous_checksum: str = ""  # Chain integrity

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ComplianceReport:
    """
    Compliance report for a period.
    """

    id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = field(default_factory=datetime.now)
    total_events: int = 0
    events_by_type: dict[str, int] = field(default_factory=dict)
    events_by_provider: dict[str, int] = field(default_factory=dict)
    policy_denials: int = 0
    quota_exceeded: int = 0
    approval_requests: int = 0
    summary: str = ""
