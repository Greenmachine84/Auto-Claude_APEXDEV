# Phase 9: Governance

> **Version**: 2.0.0 | **Duration**: Week 17-18 | **Priority**: 🟠 LOW
>
> **Status**: 📋 Specification Ready
>
> **LLM-Agnostic**: ✅ Provider-specific policies and quotas

---

## Quality Standards

| Standard | Description | Verification |
|----------|-------------|--------------|
| **World-Class** | Enterprise governance framework | Compliance audit |
| **Enterprise-Grade** | SOC 2, GDPR compliance ready | Third-party audit |
| **Fully Production Ready** | Zero policy bypass | Security testing |
| **Clean and Concise Code** | Declarative policy language | Code review |
| **Beyond PhD Level Expertise** | Advanced policy patterns | Expert assessment |

---

## Outcome Expectations

### Business Objectives

| Objective | Success Metric | World-Class Standard |
|-----------|----------------|----------------------|
| Policy enforcement | 100% coverage | Zero bypasses |
| Cost control | Quota enforcement | Budget compliance |
| Approval workflows | SLA compliance | Enterprise workflows |
| Audit trail | Complete history | Regulatory ready |

### Technical Outcomes

| Outcome | Measurement | Target | World-Class Standard |
|---------|-------------|--------|----------------------|
| Policy evaluation | P99 latency | <5ms | Zero overhead |
| Rate limit check | P99 latency | <1ms | Real-time |
| Quota calculation | Accuracy | 100% | Exact tracking |
| Approval SLA | Time to decision | <24h | Business responsive |
| Audit retrieval | Query time | <1s | Instant access |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| Policy engine works | Rule enforcement | ✅ | Dynamic rule updates |
| Approval workflows | Multi-step approvals | ✅ | Configurable flows |
| Rate limiting | Per-user/agent limits | ✅ | Per-provider limits |
| Compliance logging | Audit trail | ✅ | Immutable logs |
| Quota management | Resource limits | ✅ | Per-provider quotas |
| Provider policies | All 8 providers | ✅ | Equal governance |

---

## Acceptance Tests

| Test ID | Test Case | Pass Criteria | Verification Method |
|---------|-----------|---------------|---------------------|
| AT-9.1 | Policy denies restricted action | Request blocked | Unit test |
| AT-9.2 | Approval workflow completes | Multi-step approval | Integration test |
| AT-9.3 | Rate limit enforced | Requests throttled | Load test |
| AT-9.4 | Quota exceeded | Usage blocked | Unit test |
| AT-9.5 | Provider-specific rate limit | Per-provider limits | Integration test |
| AT-9.6 | Provider-specific quota | Per-provider cost caps | Unit test |
| AT-9.7 | Compliance log integrity | Tamper-proof | Security test |
| AT-9.8 | Policy hot-reload | No downtime update | Integration test |
| AT-9.9 | Approval expiration | Auto-expire old requests | Unit test |
| AT-9.10 | Multi-tenant isolation | Policies isolated | Security test |

---

## Performance Metrics

| Metric | Target | Measurement Method | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Policy evaluation | <5ms P99 | Prometheus | >20ms |
| Rate limit check | <1ms P99 | Prometheus | >5ms |
| Quota update | <10ms | Prometheus | >50ms |
| Approval creation | <100ms | Prometheus | >500ms |
| Audit log write | <5ms | Prometheus | >20ms |

---

## Risk Mitigations

| Risk | Impact | Mitigation | Verification |
|------|--------|------------|--------------|
| Policy bypass | Security breach | Multiple enforcement points | Pen test |
| Rate limit DoS | Service unavailable | Distributed rate limiting | Chaos test |
| Quota drift | Overspend | Real-time sync | Reconciliation |
| Approval bottleneck | Blocked workflows | Escalation rules | SLA monitoring |
| Audit tampering | Compliance failure | Append-only with checksums | Integrity audit |

---

## LLM-Agnostic Governance

### Provider-Specific Policies

```python
"""
Governance policies for ALL 8 LLM providers.
Each provider can have distinct policies.
NO default provider - all equally governed.
"""

# Provider-specific rate limits
PROVIDER_RATE_LIMITS = {
    "copilot": {"requests_per_minute": 60, "tokens_per_day": 1_000_000},
    "openrouter": {"requests_per_minute": 100, "tokens_per_day": 5_000_000},
    "ollama": {"requests_per_minute": 1000, "tokens_per_day": None},  # Local, no limit
    "lmstudio": {"requests_per_minute": 1000, "tokens_per_day": None},  # Local, no limit
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
    
    def __init__(self):
        self._provider_policies: Dict[str, ProviderPolicy] = {}
    
    async def check_provider_access(
        self,
        user_id: str,
        provider: str,
        model: str
    ) -> PolicyEvaluation:
        """
        Check if user can access a specific provider/model.
        
        Evaluates:
        1. Provider rate limits
        2. Cost quotas
        3. Model allowlists/blocklists
        4. Approval requirements
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Unknown provider: {provider}. "
                       f"Must be one of: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )
        
        policy = self._provider_policies.get(provider)
        if not policy:
            # No specific policy, allow by default
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.ALLOW,
                reason="No provider-specific policy configured"
            )
        
        # Check blocked models
        if model in policy.blocked_models:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Model {model} is blocked for provider {provider}"
            )
        
        # Check allowed models (if specified)
        if policy.allowed_models and model not in policy.allowed_models:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Model {model} not in allowed list for {provider}"
            )
        
        # Check approval requirement
        if policy.require_approval:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.REQUIRE_APPROVAL,
                reason=f"Provider {provider} requires approval"
            )
        
        return PolicyEvaluation(
            policy_id="provider_access",
            action=PolicyAction.ALLOW,
            reason="All checks passed"
        )
```

### Provider-Specific Rate Limiting

```python
class ProviderRateLimiter:
    """
    Rate limiter with per-provider limits.
    
    Each of 8 providers can have distinct rate limits.
    """
    
    async def check_provider_limit(
        self,
        user_id: str,
        provider: str
    ) -> Tuple[bool, int]:
        """
        Check rate limit for specific provider.
        
        Args:
            user_id: User making request
            provider: One of 8 LLM providers
        
        Returns:
            (allowed, remaining_requests)
        """
        limit_config = PROVIDER_RATE_LIMITS.get(provider)
        if not limit_config:
            return True, -1  # Unknown provider, allow
        
        rpm = limit_config.get("requests_per_minute")
        if rpm is None:
            return True, -1  # No limit (e.g., local providers)
        
        return await self.check(
            limit_id=f"provider:{provider}:rpm",
            target_id=user_id
        )
```

### Provider-Specific Quotas

```python
class ProviderQuotaManager:
    """
    Quota manager with per-provider limits.
    
    Tracks cost quotas for each of 8 providers separately.
    """
    
    async def check_provider_quota(
        self,
        user_id: str,
        provider: str,
        estimated_cost: float
    ) -> Tuple[bool, float]:
        """
        Check if user has remaining quota for provider.
        
        Args:
            user_id: User making request
            provider: One of 8 LLM providers
            estimated_cost: Estimated cost in USD
        
        Returns:
            (allowed, remaining_quota)
        """
        quota_config = PROVIDER_QUOTAS.get(provider)
        if not quota_config:
            return True, float("inf")
        
        monthly_limit = quota_config.get("monthly_cost_usd")
        if monthly_limit is None:
            return True, float("inf")  # No limit
        
        return await self.check(
            user_id=user_id,
            resource=f"cost:{provider}:monthly",
            amount=estimated_cost
        )
```

---

## Deliverables

| File | Purpose | LOC Estimate |
|------|---------|--------------|
| `apps/backend/governance/policy/policy_engine.py` | Core policy engine | 300 |
| `apps/backend/governance/policy/provider_policies.py` | Provider-specific | 250 |
| `apps/backend/governance/policy/rules.py` | Rule definitions | 150 |
| `apps/backend/governance/workflow/approval_workflow.py` | Approvals | 300 |
| `apps/backend/governance/limits/rate_limiter.py` | Rate limiting | 250 |
| `apps/backend/governance/limits/quota_manager.py` | Quota tracking | 250 |
| `apps/backend/governance/compliance/compliance_logger.py` | Audit logging | 200 |
| `tests/test_governance_*.py` | Governance tests | 600 |

---

## Section 1: Governance Architecture

### Task 1.1: Directory Structure

```
apps/backend/governance/
├── __init__.py
├── models.py
├── policy/
│   ├── __init__.py
│   ├── policy_engine.py
│   ├── provider_policies.py
│   └── rules.py
├── workflow/
│   ├── __init__.py
│   └── approval_workflow.py
├── limits/
│   ├── __init__.py
│   ├── rate_limiter.py
│   └── quota_manager.py
└── compliance/
    ├── __init__.py
    └── compliance_logger.py
```

### Task 1.2: Governance Models

**File**: `apps/backend/governance/models.py`

```python
"""
Governance models for enterprise policy management.

World-Class Standards:
- Provider-aware policies
- Declarative rule definitions
- Complete audit trail
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PolicyAction(Enum):
    """Actions a policy can take."""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG = "log"
    WARN = "warn"


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class PolicyRule:
    """
    Single policy rule with provider awareness.
    """
    id: str
    name: str
    description: str = ""
    field: str = ""
    operator: str = "eq"
    value: Any = None
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0
    enabled: bool = True
    # LLM-Agnostic: Optional provider filter
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
    # LLM-Agnostic: Track provider for approval
    provider: Optional[str] = None
    model: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    approvers: List[str] = field(default_factory=list)
    created_at: str = ""
    expires_at: Optional[str] = None
```

---

## Section 2: Policy Engine

### Task 2.1: Policy Engine

**File**: `apps/backend/governance/policy/policy_engine.py`

```python
"""
Policy evaluation engine with provider support.

World-Class Standards:
- Sub-5ms evaluation
- Hot-reload support
- Provider-aware rules
"""
from typing import Dict, Any, List, Optional
from ..models import Policy, PolicyRule, PolicyEvaluation, PolicyAction


class PolicyEngine:
    """
    Evaluates policies against contexts.
    
    Supports provider-specific rules for all 8 LLM providers.
    """
    
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
    
    async def evaluate(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None
    ) -> List[PolicyEvaluation]:
        """
        Evaluate all applicable policies.
        
        Args:
            context: Request context
            provider: Optional LLM provider for provider-specific rules
        """
        evaluations = []
        
        for policy in self._policies.values():
            if not policy.enabled:
                continue
            
            evaluation = await self._evaluate_policy(policy, context, provider)
            evaluations.append(evaluation)
        
        return evaluations
    
    async def _evaluate_policy(
        self,
        policy: Policy,
        context: Dict[str, Any],
        provider: Optional[str]
    ) -> PolicyEvaluation:
        """Evaluate a single policy with provider awareness."""
        rules = sorted(
            [r for r in policy.rules if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in rules:
            # Skip rules for other providers
            if rule.provider and rule.provider != provider:
                continue
            
            if await self._evaluate_rule(rule, context):
                return PolicyEvaluation(
                    policy_id=policy.id,
                    action=rule.action,
                    matched_rule=rule.id,
                    reason=rule.description,
                )
        
        return PolicyEvaluation(
            policy_id=policy.id,
            action=policy.default_action,
            reason="No rules matched",
        )
```

---

## Validation Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| LLM-Agnostic System | ✅ | Provider-specific policies |
| No Default Provider | ✅ | All providers governed equally |
| 8 Equal LLM Providers | ✅ | PROVIDER_RATE_LIMITS dictionary |
| Per-Agent LLM Assignment | ✅ | Provider tracked in approvals |
| World-Class Standards | ✅ | Quality Standards table |
| Enterprise-Grade | ✅ | SOC 2, GDPR ready |
| Production Ready | ✅ | Zero policy bypass |
| Clean Code | ✅ | Declarative policy language |
| Acceptance Tests | ✅ | AT-9.1 through AT-9.10 |
| Performance Metrics | ✅ | <5ms evaluation targets |

---

## Integration Points

| Phase | Integration | Data Flow |
|-------|-------------|-----------|
| Phase 2 | LLM Router | Provider access control |
| Phase 3 | Auth | User permissions |
| Phase 6 | Security | Audit logging |
| Phase 8 | Analytics | Quota tracking |
