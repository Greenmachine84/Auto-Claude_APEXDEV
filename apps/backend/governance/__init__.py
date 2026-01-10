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

# Compliance submodule
from .compliance import (
    AuditTrail,
    ComplianceLogger,
    ComplianceReporter,
    DataRetentionManager,
)
from .config import (
    PROVIDER_QUOTAS,
    PROVIDER_RATE_LIMITS,
    GovernanceSettings,
    get_provider_quota,
    get_provider_rate_limit,
    is_approval_required,
    validate_provider,
)

# Limits submodule
from .limits import (
    AsyncThrottle,
    LimitStorage,
    QuotaManager,
    RateLimiter,
    Throttle,
)
from .models import (
    # Constants
    SUPPORTED_PROVIDERS,
    # Approval Models
    ApprovalRequest,
    ApprovalStatus,
    ApprovalStep,
    AuditRecord,
    # Compliance Models
    ComplianceEvent,
    ComplianceEventType,
    ComplianceReport,
    LimitType,
    Policy,
    # Enums
    PolicyAction,
    PolicyEvaluation,
    # Policy Models
    PolicyRule,
    Quota,
    QuotaUsage,
    # Limit Models
    RateLimit,
    RateLimitResult,
    RuleOperator,
    WorkflowDefinition,
)

# Policy submodule
from .policy import (
    ConditionEvaluator,
    PolicyEngine,
    PolicyLoader,
    ProviderPolicy,
    ProviderPolicyEngine,
    RuleBuilder,
    RuleParser,
    RuleValidator,
)

# Workflow submodule
from .workflow import (
    ApprovalDecision,
    ApprovalRequestManager,
    ApprovalWorkflow,
    EscalationManager,
    WorkflowRegistry,
    WorkflowType,
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
