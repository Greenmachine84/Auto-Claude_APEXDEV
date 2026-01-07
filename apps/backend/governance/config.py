"""
Governance Configuration - Phase 9 Implementation.

Configuration settings for governance policies, rate limits, and quotas.

World-Class Standards:
- Environment-aware configuration
- Provider-specific defaults
- Easy override via env vars

LLM-Agnostic: Configures all 8 providers equally.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
import os
import logging


logger = logging.getLogger(__name__)


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
# PROVIDER-SPECIFIC RATE LIMITS
# =============================================================================

PROVIDER_RATE_LIMITS: Dict[str, Dict[str, Optional[int]]] = {
    "copilot": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "tokens_per_day": 1_000_000,
    },
    "openrouter": {
        "requests_per_minute": 100,
        "requests_per_hour": 2000,
        "tokens_per_day": 5_000_000,
    },
    "ollama": {
        "requests_per_minute": 1000,  # Local, generous limit
        "requests_per_hour": None,    # No hourly limit
        "tokens_per_day": None,       # No token limit (local)
    },
    "lmstudio": {
        "requests_per_minute": 1000,  # Local, generous limit
        "requests_per_hour": None,    # No hourly limit
        "tokens_per_day": None,       # No token limit (local)
    },
    "gemini": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "tokens_per_day": 2_000_000,
    },
    "openai": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "tokens_per_day": 2_000_000,
    },
    "anthropic": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "tokens_per_day": 2_000_000,
    },
    "azure": {
        "requests_per_minute": 100,
        "requests_per_hour": 2000,
        "tokens_per_day": 5_000_000,
    },
}


# =============================================================================
# PROVIDER-SPECIFIC COST QUOTAS
# =============================================================================

PROVIDER_QUOTAS: Dict[str, Dict[str, Optional[float]]] = {
    "copilot": {
        "monthly_cost_usd": None,     # Subscription-based, no per-use cost
        "daily_cost_usd": None,
    },
    "openrouter": {
        "monthly_cost_usd": 100.0,
        "daily_cost_usd": 10.0,
    },
    "ollama": {
        "monthly_cost_usd": None,     # Free (local)
        "daily_cost_usd": None,
    },
    "lmstudio": {
        "monthly_cost_usd": None,     # Free (local)
        "daily_cost_usd": None,
    },
    "gemini": {
        "monthly_cost_usd": 50.0,
        "daily_cost_usd": 5.0,
    },
    "openai": {
        "monthly_cost_usd": 100.0,
        "daily_cost_usd": 10.0,
    },
    "anthropic": {
        "monthly_cost_usd": 100.0,
        "daily_cost_usd": 10.0,
    },
    "azure": {
        "monthly_cost_usd": 200.0,
        "daily_cost_usd": 20.0,
    },
}


# =============================================================================
# PROVIDER APPROVAL REQUIREMENTS
# =============================================================================

PROVIDER_APPROVAL_REQUIRED: Dict[str, bool] = {
    "copilot": False,      # No approval needed
    "openrouter": False,   # No approval needed
    "ollama": False,       # No approval needed (local)
    "lmstudio": False,     # No approval needed (local)
    "gemini": False,       # No approval needed
    "openai": False,       # No approval needed
    "anthropic": False,    # No approval needed
    "azure": True,         # Enterprise - approval required
}


# =============================================================================
# DEFAULT GOVERNANCE SETTINGS
# =============================================================================

@dataclass
class GovernanceSettings:
    """
    Central governance configuration.
    """
    # Policy Engine
    policy_evaluation_enabled: bool = True
    policy_cache_ttl_seconds: int = 300
    policy_hot_reload_enabled: bool = True
    
    # Rate Limiting
    rate_limiting_enabled: bool = True
    rate_limit_storage: str = "memory"  # "memory", "redis", "sqlite"
    rate_limit_sync_interval_seconds: int = 5
    
    # Quota Management
    quota_enforcement_enabled: bool = True
    quota_warning_threshold_percent: float = 80.0
    quota_storage: str = "memory"
    
    # Approval Workflows
    approval_workflows_enabled: bool = True
    approval_default_timeout_hours: int = 24
    approval_reminder_hours: int = 4
    approval_auto_escalate: bool = True
    
    # Compliance Logging
    compliance_logging_enabled: bool = True
    compliance_log_retention_days: int = 90
    compliance_log_storage: str = "file"  # "file", "database"
    compliance_checksum_enabled: bool = True
    
    # Performance
    max_policies_cached: int = 1000
    max_rules_per_policy: int = 100
    evaluation_timeout_ms: int = 50
    
    @classmethod
    def from_env(cls) -> "GovernanceSettings":
        """Load settings from environment variables."""
        return cls(
            policy_evaluation_enabled=os.getenv(
                "GOVERNANCE_POLICY_ENABLED", "true"
            ).lower() == "true",
            rate_limiting_enabled=os.getenv(
                "GOVERNANCE_RATE_LIMIT_ENABLED", "true"
            ).lower() == "true",
            rate_limit_storage=os.getenv(
                "GOVERNANCE_RATE_LIMIT_STORAGE", "memory"
            ),
            quota_enforcement_enabled=os.getenv(
                "GOVERNANCE_QUOTA_ENABLED", "true"
            ).lower() == "true",
            quota_warning_threshold_percent=float(os.getenv(
                "GOVERNANCE_QUOTA_WARNING_THRESHOLD", "80.0"
            )),
            approval_workflows_enabled=os.getenv(
                "GOVERNANCE_APPROVAL_ENABLED", "true"
            ).lower() == "true",
            approval_default_timeout_hours=int(os.getenv(
                "GOVERNANCE_APPROVAL_TIMEOUT_HOURS", "24"
            )),
            compliance_logging_enabled=os.getenv(
                "GOVERNANCE_COMPLIANCE_ENABLED", "true"
            ).lower() == "true",
            compliance_log_retention_days=int(os.getenv(
                "GOVERNANCE_LOG_RETENTION_DAYS", "90"
            )),
        )


# =============================================================================
# DEFAULT POLICIES
# =============================================================================

DEFAULT_POLICIES = [
    {
        "id": "default_allow",
        "name": "Default Allow Policy",
        "description": "Allows all requests by default",
        "rules": [],
        "default_action": "allow",
        "enabled": True,
    },
    {
        "id": "provider_access",
        "name": "Provider Access Control",
        "description": "Controls access to LLM providers",
        "rules": [
            {
                "id": "block_unknown_provider",
                "name": "Block Unknown Providers",
                "field": "provider",
                "operator": "not_in",
                "value": SUPPORTED_PROVIDERS,
                "action": "deny",
                "priority": 100,
            }
        ],
        "default_action": "allow",
        "enabled": True,
    },
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_provider_rate_limit(
    provider: str,
    limit_type: str = "requests_per_minute"
) -> Optional[int]:
    """Get rate limit for a provider."""
    if provider not in PROVIDER_RATE_LIMITS:
        logger.warning(f"Unknown provider: {provider}")
        return None
    return PROVIDER_RATE_LIMITS[provider].get(limit_type)


def get_provider_quota(
    provider: str,
    quota_type: str = "monthly_cost_usd"
) -> Optional[float]:
    """Get quota limit for a provider."""
    if provider not in PROVIDER_QUOTAS:
        logger.warning(f"Unknown provider: {provider}")
        return None
    return PROVIDER_QUOTAS[provider].get(quota_type)


def is_approval_required(provider: str) -> bool:
    """Check if provider requires approval."""
    return PROVIDER_APPROVAL_REQUIRED.get(provider, False)


def validate_provider(provider: str) -> bool:
    """Validate provider is in supported list."""
    return provider in SUPPORTED_PROVIDERS
