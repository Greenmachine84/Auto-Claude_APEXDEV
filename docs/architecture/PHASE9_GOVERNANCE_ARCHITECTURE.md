# Phase 9: Governance Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 9 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Reference: `docs/specs/phase-09-governance.md`

---

## Overview

Phase 9 implements enterprise governance including policy engine, approval workflows, rate limiting, and quota management. All governance is **LLM-Agnostic** with provider-specific policies and quotas for all 8 supported providers.

---

## Quality Standards

| Standard | Target | Verification |
|----------|--------|-------------|
| Zero Policy Bypass | 100% | Security testing |
| SOC 2/GDPR Ready | ✅ | Third-party audit |
| Sub-5ms Policy Eval | P99 | Performance testing |
| Declarative Policies | ✅ | Code review |

---

## LLM-Agnostic Governance Design

> **CRITICAL**: Governance policies apply equally to ALL 8 LLM providers.
> Each provider can have distinct rate limits, quotas, and approval requirements.
> NO default provider - all governed equally.

### Provider-Specific Governance
| Provider | Rate Limit | Quota | Approval |
|----------|------------|-------|----------|
| copilot | 60 rpm | Subscription | Optional |
| openrouter | 100 rpm | $100/mo | Optional |
| ollama | 1000 rpm | None | None |
| lmstudio | 1000 rpm | None | None |
| gemini | 60 rpm | $50/mo | Optional |
| openai | 60 rpm | $100/mo | Optional |
| anthropic | 60 rpm | $100/mo | Optional |
| azure | 100 rpm | $200/mo | Required |

---

## Directory Structure

```
apps/
└── backend/
    └── governance/
        ├── __init__.py                    # Governance module exports
        ├── models.py                      # Governance data models
        ├── config.py                      # Governance configuration
        │
        ├── policy/
        │   ├── __init__.py                # Policy exports
        │   ├── policy_engine.py           # Core policy evaluation
        │   ├── provider_policies.py       # Provider-specific policies
        │   ├── rules.py                   # Rule definitions
        │   ├── conditions.py              # Condition evaluators
        │   └── policy_loader.py           # Policy loading/hot-reload
        │
        ├── workflow/
        │   ├── __init__.py                # Workflow exports
        │   ├── approval_workflow.py       # Approval workflow engine
        │   ├── workflow_definitions.py    # Workflow templates
        │   ├── approval_request.py        # Approval request management
        │   └── escalation.py              # Escalation rules
        │
        ├── limits/
        │   ├── __init__.py                # Limits exports
        │   ├── rate_limiter.py            # Per-provider rate limiting
        │   ├── quota_manager.py           # Per-provider quota tracking
        │   ├── throttle.py                # Request throttling
        │   └── limit_storage.py           # Limit state persistence
        │
        └── compliance/
            ├── __init__.py                # Compliance exports
            ├── compliance_logger.py       # Compliance event logging
            ├── audit_trail.py             # Governance audit trail
            ├── reporting.py               # Compliance reporting
            └── data_retention.py          # Data retention policies
```

---

## File Specifications

### 1. Governance Core (`governance/`)

#### `models.py`
**Purpose**: Governance domain models
**Key Components**:
```python
class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG = "log"
    WARN = "warn"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class PolicyRule:
    """Single policy rule with provider awareness."""
    id: str
    name: str
    description: str = ""
    field: str = ""
    operator: str = "eq"
    value: Any = None
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0
    enabled: bool = True
    provider: Optional[str] = None  # Apply only to specific provider


@dataclass
class Policy:
    """Collection of rules for governance."""
    id: str
    name: str
    description: str = ""
    rules: List[PolicyRule] = field(default_factory=list)
    default_action: PolicyAction = PolicyAction.ALLOW
    enabled: bool = True
    applies_to: List[str] = field(default_factory=list)


@dataclass
class ApprovalRequest:
    """Request requiring approval with provider context."""
    id: str
    request_type: str
    requester_id: str
    description: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    provider: Optional[str] = None  # Track provider for approval
    model: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    approvers: List[str] = field(default_factory=list)
    created_at: str = ""
    expires_at: Optional[str] = None


@dataclass
class PolicyEvaluation:
    """Result of policy evaluation."""
    policy_id: str
    action: PolicyAction
    reason: str
    matched_rule: Optional[str] = None
```

#### `config.py`
**Purpose**: Governance configuration
**Key Components**:
```python
# Provider-specific rate limits
PROVIDER_RATE_LIMITS = {
    "copilot": {"requests_per_minute": 60, "tokens_per_day": 1_000_000},
    "openrouter": {"requests_per_minute": 100, "tokens_per_day": 5_000_000},
    "ollama": {"requests_per_minute": 1000, "tokens_per_day": None},  # Local
    "lmstudio": {"requests_per_minute": 1000, "tokens_per_day": None},  # Local
    "gemini": {"requests_per_minute": 60, "tokens_per_day": 2_000_000},
    "openai": {"requests_per_minute": 60, "tokens_per_day": 2_000_000},
    "anthropic": {"requests_per_minute": 60, "tokens_per_day": 2_000_000},
    "azure": {"requests_per_minute": 100, "tokens_per_day": 5_000_000},
}

# Provider-specific cost quotas
PROVIDER_QUOTAS = {
    "copilot": {"monthly_cost_usd": None},  # Subscription
    "openrouter": {"monthly_cost_usd": 100.0},
    "ollama": {"monthly_cost_usd": None},  # Free
    "lmstudio": {"monthly_cost_usd": None},  # Free
    "gemini": {"monthly_cost_usd": 50.0},
    "openai": {"monthly_cost_usd": 100.0},
    "anthropic": {"monthly_cost_usd": 100.0},
    "azure": {"monthly_cost_usd": 200.0},
}
```

---

### 2. Policy Module (`governance/policy/`)

#### `policy_engine.py`
**Purpose**: Core policy evaluation engine
**Key Components**:
```python
class PolicyEngine:
    """
    Evaluates policies against contexts.
    
    Supports provider-specific rules for all 8 LLM providers.
    """
    
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
    
    async def evaluate(self, context: Dict[str, Any], 
                       provider: Optional[str] = None) -> List[PolicyEvaluation]
    
    async def check_provider_access(self, user_id: str, provider: str, 
                                     model: str) -> PolicyEvaluation
    
    def register_policy(self, policy: Policy) -> None
    def unregister_policy(self, policy_id: str) -> None
    def reload_policies(self) -> None
```

#### `provider_policies.py`
**Purpose**: Provider-specific policy definitions
**Key Components**:
```python
@dataclass
class ProviderPolicy:
    """Policy specific to an LLM provider."""
    provider: str  # One of 8 providers
    rate_limit: Optional[RateLimit] = None
    cost_quota: Optional[Quota] = None
    allowed_models: List[str] = field(default_factory=list)
    blocked_models: List[str] = field(default_factory=list)
    require_approval: bool = False


class ProviderPolicyEngine:
    """
    Policy engine with provider-specific rules.
    
    Enforces governance for all 8 LLM providers equally.
    """
    
    SUPPORTED_PROVIDERS = [
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    ]
    
    async def check_provider_access(self, user_id: str, provider: str, 
                                     model: str) -> PolicyEvaluation
    async def enforce_rate_limit(self, user_id: str, provider: str) -> bool
    async def check_quota(self, user_id: str, provider: str, 
                          estimated_cost: float) -> bool
```

#### `rules.py`
**Purpose**: Rule definition and parsing
**Key Components**:
- Rule DSL parsing
- Condition operators
- Rule validation

#### `conditions.py`
**Purpose**: Condition evaluation
**Key Components**:
```python
class ConditionEvaluator:
    def evaluate(self, condition: str, context: Dict) -> bool
    def evaluate_provider_condition(self, provider: str, context: Dict) -> bool
```

#### `policy_loader.py`
**Purpose**: Load policies from files/database
**Key Components**:
- YAML/JSON policy loading
- Database policy loading
- Hot-reload support

---

### 3. Workflow Module (`governance/workflow/`)

#### `approval_workflow.py`
**Purpose**: Approval workflow engine
**Key Components**:
```python
class ApprovalWorkflow:
    async def create_request(self, request: ApprovalRequest) -> str
    async def approve(self, request_id: str, approver_id: str) -> bool
    async def reject(self, request_id: str, approver_id: str, reason: str) -> bool
    async def get_pending(self, approver_id: str) -> List[ApprovalRequest]
    async def check_status(self, request_id: str) -> ApprovalStatus
```

#### `workflow_definitions.py`
**Purpose**: Workflow templates
**Key Components**:
- Single-approver workflow
- Multi-approver workflow
- Chain approval workflow

#### `escalation.py`
**Purpose**: Escalation rules
**Key Components**:
```python
class EscalationEngine:
    def check_escalation(self, request: ApprovalRequest) -> bool
    def escalate(self, request_id: str) -> None
    def configure_escalation(self, timeout_hours: int, escalation_path: List[str]) -> None
```

---

### 4. Limits Module (`governance/limits/`)

#### `rate_limiter.py`
**Purpose**: Per-provider rate limiting
**Key Components**:
```python
class ProviderRateLimiter:
    """
    Rate limiter with per-provider limits.
    
    Each of 8 providers can have distinct rate limits.
    """
    
    async def check_provider_limit(self, user_id: str, 
                                    provider: str) -> Tuple[bool, int]:
        """
        Check rate limit for specific provider.
        
        Args:
            user_id: User making request
            provider: One of 8 LLM providers
        
        Returns:
            (allowed, remaining_requests)
        """
        pass
    
    async def record_request(self, user_id: str, provider: str) -> None
    async def get_remaining(self, user_id: str, provider: str) -> int
    async def reset_limit(self, user_id: str, provider: str) -> None
```

#### `quota_manager.py`
**Purpose**: Per-provider quota tracking
**Key Components**:
```python
class ProviderQuotaManager:
    """
    Quota manager with per-provider limits.
    
    Tracks cost quotas for each of 8 providers separately.
    """
    
    async def check_provider_quota(self, user_id: str, provider: str,
                                    estimated_cost: float) -> Tuple[bool, float]:
        """
        Check if user has remaining quota for provider.
        
        Returns:
            (allowed, remaining_quota)
        """
        pass
    
    async def consume_quota(self, user_id: str, provider: str, amount: float) -> None
    async def get_usage(self, user_id: str, provider: str) -> float
    async def reset_quota(self, user_id: str, provider: str) -> None
```

#### `throttle.py`
**Purpose**: Request throttling
**Key Components**:
- Token bucket algorithm
- Sliding window
- Backoff strategies

#### `limit_storage.py`
**Purpose**: Persist limit state
**Key Components**:
- Redis integration
- SQLite fallback
- Distributed locking

---

### 5. Compliance Module (`governance/compliance/`)

#### `compliance_logger.py`
**Purpose**: Compliance event logging
**Key Components**:
```python
class ComplianceLogger:
    def log_policy_evaluation(self, evaluation: PolicyEvaluation) -> None
    def log_approval_action(self, request_id: str, action: str, actor: str) -> None
    def log_rate_limit_hit(self, user_id: str, provider: str) -> None
    def log_quota_exceeded(self, user_id: str, provider: str) -> None
```

#### `audit_trail.py`
**Purpose**: Governance audit trail
**Key Components**:
- Immutable audit records
- Integrity verification
- Query interface

#### `reporting.py`
**Purpose**: Compliance reporting
**Key Components**:
```python
class ComplianceReporter:
    def generate_policy_report(self, period: str) -> ComplianceReport
    def generate_approval_report(self, period: str) -> ApprovalReport
    def generate_quota_report(self, period: str) -> QuotaReport
    def export_report(self, report: Any, format: str) -> bytes
```

#### `data_retention.py`
**Purpose**: Data retention policies
**Key Components**:
- Configurable retention periods
- Automatic cleanup
- GDPR compliance

---

## Integration Points

### With LLM Layer (Phase 2)
- Rate limits applied at LLM router level
- Quota checks before LLM calls

### With Security (Phase 6)
- RBAC integrated with policy engine
- Audit logs feed compliance

### With Analytics (Phase 8)
- Usage data informs quota enforcement
- Cost tracking enables budget enforcement

### With Agents (Phase 7)
- Agent actions subject to policies
- Approval workflows for sensitive operations

---

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Policy evaluation | <5ms P99 | >20ms |
| Rate limit check | <1ms P99 | >5ms |
| Quota update | <10ms | >50ms |
| Approval creation | <100ms | >500ms |
| Audit log write | <5ms | >20ms |

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `governance/` (core) | 3 | Governance core |
| `governance/policy/` | 6 | Policy engine |
| `governance/workflow/` | 5 | Approval workflows |
| `governance/limits/` | 5 | Rate limiting/quotas |
| `governance/compliance/` | 5 | Compliance logging |
| **Total** | **24** | Phase 9 files |

---

## Next Steps

→ Phase 10: Testing & Documentation Architecture

---

*Phase 9 Architecture complete. 24 files specified for governance module.*
