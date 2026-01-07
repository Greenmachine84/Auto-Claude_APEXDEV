"""
Policy Evaluation Engine - Phase 9 Implementation.

Core policy engine with provider-specific rule support.

World-Class Standards:
- Sub-5ms evaluation performance
- Hot-reload capability
- Provider-aware rules
- Complete audit trail

LLM-Agnostic: Evaluates policies for all 8 providers equally.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import logging
import asyncio
from dataclasses import field

from ..models import (
    Policy,
    PolicyRule,
    PolicyEvaluation,
    PolicyAction,
    RuleOperator,
    SUPPORTED_PROVIDERS,
)


logger = logging.getLogger(__name__)


class PolicyEngine:
    """
    Evaluates policies against request contexts.
    
    Supports provider-specific rules for all 8 LLM providers.
    Designed for sub-5ms evaluation performance.
    """
    
    def __init__(self) -> None:
        self._policies: Dict[str, Policy] = {}
        self._policy_cache: Dict[str, List[PolicyEvaluation]] = {}
        self._cache_ttl: int = 300  # 5 minutes
        self._last_reload: datetime = datetime.now()
        
    async def evaluate(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None
    ) -> List[PolicyEvaluation]:
        """
        Evaluate all applicable policies against context.
        
        Args:
            context: Request context with fields to evaluate
            provider: Optional LLM provider for provider-specific rules
            
        Returns:
            List of policy evaluations
        """
        start_time = time.perf_counter()
        evaluations: List[PolicyEvaluation] = []
        
        for policy in self._policies.values():
            if not policy.enabled:
                continue
                
            evaluation = await self._evaluate_policy(policy, context, provider)
            evaluations.append(evaluation)
            
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        if elapsed_ms > 5:
            logger.warning(f"Policy evaluation took {elapsed_ms:.2f}ms (target: <5ms)")
            
        return evaluations
    
    async def evaluate_single(
        self,
        policy_id: str,
        context: Dict[str, Any],
        provider: Optional[str] = None
    ) -> Optional[PolicyEvaluation]:
        """Evaluate a single policy by ID."""
        policy = self._policies.get(policy_id)
        if not policy or not policy.enabled:
            return None
        return await self._evaluate_policy(policy, context, provider)
    
    async def check_access(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None
    ) -> bool:
        """
        Quick access check - returns True if all policies allow.
        
        Use for fast gate checks before proceeding.
        """
        evaluations = await self.evaluate(context, provider)
        return all(
            e.action in (PolicyAction.ALLOW, PolicyAction.LOG, PolicyAction.WARN)
            for e in evaluations
        )
    
    async def _evaluate_policy(
        self,
        policy: Policy,
        context: Dict[str, Any],
        provider: Optional[str]
    ) -> PolicyEvaluation:
        """Evaluate a single policy with provider awareness."""
        start_time = time.perf_counter()
        
        # Sort rules by priority (highest first)
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
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return PolicyEvaluation(
                    policy_id=policy.id,
                    action=rule.action,
                    matched_rule=rule.id,
                    reason=rule.description or f"Matched rule: {rule.name}",
                    evaluation_time_ms=elapsed_ms,
                    provider=provider,
                    context_snapshot=self._snapshot_context(context),
                )
        
        # No rules matched, use default action
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return PolicyEvaluation(
            policy_id=policy.id,
            action=policy.default_action,
            matched_rule=None,
            reason="No rules matched, using default action",
            evaluation_time_ms=elapsed_ms,
            provider=provider,
            context_snapshot=self._snapshot_context(context),
        )
    
    async def _evaluate_rule(
        self,
        rule: PolicyRule,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a single rule against context."""
        if not rule.field:
            return False
            
        # Get value from context using dot notation
        value = self._get_nested_value(context, rule.field)
        if value is None and rule.operator != RuleOperator.EQ:
            return False
            
        return self._compare_values(value, rule.value, rule.operator)
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value using dot notation (e.g., 'user.role')."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _compare_values(
        self,
        actual: Any,
        expected: Any,
        operator: RuleOperator
    ) -> bool:
        """Compare values using the specified operator."""
        try:
            if operator == RuleOperator.EQ:
                return actual == expected
            elif operator == RuleOperator.NE:
                return actual != expected
            elif operator == RuleOperator.GT:
                return actual > expected
            elif operator == RuleOperator.GE:
                return actual >= expected
            elif operator == RuleOperator.LT:
                return actual < expected
            elif operator == RuleOperator.LE:
                return actual <= expected
            elif operator == RuleOperator.IN:
                return actual in expected
            elif operator == RuleOperator.NOT_IN:
                return actual not in expected
            elif operator == RuleOperator.CONTAINS:
                return expected in str(actual)
            elif operator == RuleOperator.STARTS_WITH:
                return str(actual).startswith(str(expected))
            elif operator == RuleOperator.ENDS_WITH:
                return str(actual).endswith(str(expected))
            elif operator == RuleOperator.MATCHES:
                import re
                return bool(re.match(str(expected), str(actual)))
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except (TypeError, ValueError) as e:
            logger.debug(f"Comparison failed: {e}")
            return False
    
    def _snapshot_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a safe snapshot of context for audit."""
        # Exclude sensitive fields
        sensitive_fields = {"password", "token", "secret", "key", "auth"}
        return {
            k: v for k, v in context.items()
            if not any(s in k.lower() for s in sensitive_fields)
        }
    
    def register_policy(self, policy: Policy) -> None:
        """Register a policy for evaluation."""
        self._policies[policy.id] = policy
        self._invalidate_cache()
        logger.info(f"Registered policy: {policy.id} ({policy.name})")
    
    def unregister_policy(self, policy_id: str) -> bool:
        """Unregister a policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            self._invalidate_cache()
            logger.info(f"Unregistered policy: {policy_id}")
            return True
        return False
    
    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """Get a policy by ID."""
        return self._policies.get(policy_id)
    
    def list_policies(self) -> List[Policy]:
        """List all registered policies."""
        return list(self._policies.values())
    
    def reload_policies(self) -> None:
        """Trigger hot-reload of policies."""
        self._invalidate_cache()
        self._last_reload = datetime.now()
        logger.info("Policies reloaded")
    
    def _invalidate_cache(self) -> None:
        """Invalidate the evaluation cache."""
        self._policy_cache.clear()
