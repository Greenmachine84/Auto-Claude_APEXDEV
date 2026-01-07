"""
Provider-Specific Policies - Phase 9 Implementation.

Policy definitions and enforcement for all 8 LLM providers.

World-Class Standards:
- Equal treatment for all providers
- Configurable per-provider rules
- Model allowlist/blocklist support

LLM-Agnostic: No default provider, all governed equally.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..models import (
    PolicyEvaluation,
    PolicyAction,
    RateLimit,
    Quota,
    SUPPORTED_PROVIDERS,
)
from ..config import (
    PROVIDER_RATE_LIMITS,
    PROVIDER_QUOTAS,
    PROVIDER_APPROVAL_REQUIRED,
)


logger = logging.getLogger(__name__)


@dataclass
class ProviderPolicy:
    """
    Policy specific to an LLM provider.
    
    Defines access control, rate limits, quotas, and model restrictions
    for a single provider.
    """
    provider: str  # One of 8 supported providers
    enabled: bool = True
    rate_limit: Optional[RateLimit] = None
    cost_quota: Optional[Quota] = None
    allowed_models: List[str] = field(default_factory=list)
    blocked_models: List[str] = field(default_factory=list)
    require_approval: bool = False
    max_tokens_per_request: Optional[int] = None
    allowed_users: List[str] = field(default_factory=list)  # Empty = all
    blocked_users: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )


class ProviderPolicyEngine:
    """
    Policy engine with provider-specific rules.
    
    Enforces governance for all 8 LLM providers equally.
    Each provider can have distinct policies while maintaining
    consistent governance framework.
    """
    
    SUPPORTED_PROVIDERS = SUPPORTED_PROVIDERS
    
    def __init__(self) -> None:
        self._provider_policies: Dict[str, ProviderPolicy] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default policies for all providers."""
        for provider in self.SUPPORTED_PROVIDERS:
            self._provider_policies[provider] = ProviderPolicy(
                provider=provider,
                enabled=True,
                require_approval=PROVIDER_APPROVAL_REQUIRED.get(provider, False),
            )
    
    async def check_provider_access(
        self,
        user_id: str,
        provider: str,
        model: str
    ) -> PolicyEvaluation:
        """
        Check if user can access a specific provider/model.
        
        Evaluates:
        1. Provider enabled status
        2. User allowlist/blocklist
        3. Model allowlist/blocklist
        4. Approval requirements
        
        Args:
            user_id: User making request
            provider: One of 8 LLM providers
            model: Model identifier
            
        Returns:
            PolicyEvaluation with allow/deny decision
        """
        # Validate provider
        if provider not in self.SUPPORTED_PROVIDERS:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Unknown provider: {provider}. "
                       f"Must be one of: {', '.join(self.SUPPORTED_PROVIDERS)}",
                provider=provider,
            )
        
        policy = self._provider_policies.get(provider)
        
        # No specific policy configured
        if not policy:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.ALLOW,
                reason="No provider-specific policy configured",
                provider=provider,
            )
        
        # Provider disabled
        if not policy.enabled:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Provider {provider} is disabled",
                provider=provider,
            )
        
        # Check blocked users
        if policy.blocked_users and user_id in policy.blocked_users:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"User {user_id} is blocked from provider {provider}",
                provider=provider,
            )
        
        # Check allowed users (if specified)
        if policy.allowed_users and user_id not in policy.allowed_users:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"User {user_id} not in allowed list for {provider}",
                provider=provider,
            )
        
        # Check blocked models
        if model in policy.blocked_models:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Model {model} is blocked for provider {provider}",
                provider=provider,
            )
        
        # Check allowed models (if specified)
        if policy.allowed_models and model not in policy.allowed_models:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.DENY,
                reason=f"Model {model} not in allowed list for {provider}",
                provider=provider,
            )
        
        # Check approval requirement
        if policy.require_approval:
            return PolicyEvaluation(
                policy_id="provider_access",
                action=PolicyAction.REQUIRE_APPROVAL,
                reason=f"Provider {provider} requires approval",
                provider=provider,
            )
        
        return PolicyEvaluation(
            policy_id="provider_access",
            action=PolicyAction.ALLOW,
            reason="All access checks passed",
            provider=provider,
        )
    
    def set_provider_policy(self, policy: ProviderPolicy) -> None:
        """Set or update policy for a provider."""
        self._provider_policies[policy.provider] = policy
        logger.info(f"Updated policy for provider: {policy.provider}")
    
    def get_provider_policy(self, provider: str) -> Optional[ProviderPolicy]:
        """Get policy for a specific provider."""
        return self._provider_policies.get(provider)
    
    def enable_provider(self, provider: str) -> bool:
        """Enable a provider."""
        if provider not in self._provider_policies:
            return False
        self._provider_policies[provider].enabled = True
        logger.info(f"Enabled provider: {provider}")
        return True
    
    def disable_provider(self, provider: str) -> bool:
        """Disable a provider."""
        if provider not in self._provider_policies:
            return False
        self._provider_policies[provider].enabled = False
        logger.info(f"Disabled provider: {provider}")
        return True
    
    def block_model(self, provider: str, model: str) -> bool:
        """Block a specific model for a provider."""
        policy = self._provider_policies.get(provider)
        if not policy:
            return False
        if model not in policy.blocked_models:
            policy.blocked_models.append(model)
            logger.info(f"Blocked model {model} for provider {provider}")
        return True
    
    def unblock_model(self, provider: str, model: str) -> bool:
        """Unblock a specific model for a provider."""
        policy = self._provider_policies.get(provider)
        if not policy:
            return False
        if model in policy.blocked_models:
            policy.blocked_models.remove(model)
            logger.info(f"Unblocked model {model} for provider {provider}")
        return True
    
    def set_allowed_models(self, provider: str, models: List[str]) -> bool:
        """Set allowed models for a provider (empty = all allowed)."""
        policy = self._provider_policies.get(provider)
        if not policy:
            return False
        policy.allowed_models = models
        logger.info(f"Set allowed models for {provider}: {models}")
        return True
    
    def require_approval_for_provider(
        self,
        provider: str,
        require: bool = True
    ) -> bool:
        """Set approval requirement for a provider."""
        policy = self._provider_policies.get(provider)
        if not policy:
            return False
        policy.require_approval = require
        logger.info(f"Set approval required for {provider}: {require}")
        return True
    
    def list_enabled_providers(self) -> List[str]:
        """List all enabled providers."""
        return [
            p for p, policy in self._provider_policies.items()
            if policy.enabled
        ]
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            provider: {
                "enabled": policy.enabled,
                "require_approval": policy.require_approval,
                "allowed_models_count": len(policy.allowed_models),
                "blocked_models_count": len(policy.blocked_models),
            }
            for provider, policy in self._provider_policies.items()
        }
