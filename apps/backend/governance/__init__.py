"""
Governance Module - Phase 9 Implementation.

Enterprise-grade governance for LLM provider management.

Components:
- Policy Engine: Rule-based access control
- Approval Workflows: Multi-step approval processes  
- Rate Limiting: Provider-aware rate limits
- Quota Management: Cost tracking and quotas
- Compliance Logging: SOC 2/GDPR ready audit trail

Supported Providers (8):
- copilot, openrouter, ollama, lmstudio
- gemini, openai, anthropic, azure
"""

from .models import (
    # Enums
    PolicyAction,
    ApprovalStatus,
    RuleOperator,
    LimitType,
    ComplianceEventType,
    # Policy Models
    PolicyRule,
    Policy,
    PolicyEvaluation,
    # Approval Models
    ApprovalRequest,
    ApprovalStep,
    WorkflowDefinition,
    # Limit Models
    RateLimit,
    RateLimitResult,
    Quota,
    QuotaUsage,
    # Compliance Models
    ComplianceEvent,
    AuditRecord,
    ComplianceReport,
    # Constants
    SUPPORTED_PROVIDERS,
)

from .config import (
    PROVIDER_RATE_LIMITS,
    PROVIDER_QUOTAS,
    GovernanceSettings,
    get_provider_rate_limit,
    get_provider_quota,
    is_approval_required,
    validate_provider,
)

# Policy submodule
from .policy import (
    PolicyEngine,
    ProviderPolicy,
    ProviderPolicyEngine,
    RuleParser,
    RuleValidator,
    RuleBuilder,
    ConditionEvaluator,
    PolicyLoader,
)

# Workflow submodule
from .workflow import (
    ApprovalWorkflow,
    WorkflowType,
    WorkflowRegistry,
    ApprovalDecision,
    ApprovalRequestManager,
    EscalationManager,
)

# Limits submodule
from .limits import (
    RateLimiter,
    QuotaManager,
    Throttle,
    AsyncThrottle,
    LimitStorage,
)

# Compliance submodule
from .compliance import (
    ComplianceLogger,
    AuditTrail,
    ComplianceReporter,
    DataRetentionManager,
)


__all__ = [
    # Models
    "PolicyAction",
    "ApprovalStatus",
    "RuleOperator",
    "LimitType",
    "ComplianceEventType",
    "PolicyRule",
    "Policy",
    "PolicyEvaluation",
    "ApprovalRequest",
    "ApprovalStep",
    "WorkflowDefinition",
    "RateLimit",
    "RateLimitResult",
    "Quota",
    "QuotaUsage",
    "ComplianceEvent",
    "AuditRecord",
    "ComplianceReport",
    "SUPPORTED_PROVIDERS",
    # Config
    "PROVIDER_RATE_LIMITS",
    "PROVIDER_QUOTAS",
    "GovernanceSettings",
    "get_provider_rate_limit",
    "get_provider_quota",
    "is_approval_required",
    "validate_provider",
    # Policy
    "PolicyEngine",
    "ProviderPolicy",
    "ProviderPolicyEngine",
    "RuleParser",
    "RuleValidator",
    "RuleBuilder",
    "ConditionEvaluator",
    "PolicyLoader",
    # Workflow
    "ApprovalWorkflow",
    "WorkflowType",
    "WorkflowRegistry",
    "ApprovalDecision",
    "ApprovalRequestManager",
    "EscalationManager",
    # Limits
    "RateLimiter",
    "QuotaManager",
    "Throttle",
    "AsyncThrottle",
    "LimitStorage",
    # Compliance
    "ComplianceLogger",
    "AuditTrail",
    "ComplianceReporter",
    "DataRetentionManager",
]


__version__ = "1.0.0"
__phase__ = 9
