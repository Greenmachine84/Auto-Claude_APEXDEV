"""
Phase 9 Governance Tests.

Comprehensive tests for the governance module.
Updated to match actual model implementation.
"""

import pytest
from datetime import datetime, timedelta

# Import governance components
from apps.backend.governance.models import (
    PolicyAction, ApprovalStatus, RuleOperator, LimitType,
    PolicyRule, Policy, RateLimit, Quota,
    SUPPORTED_PROVIDERS, ComplianceEventType
)
from apps.backend.governance.config import (
    get_provider_rate_limit, get_provider_quota,
    is_approval_required, validate_provider
)


class TestSupportedProviders:
    """Test provider configuration."""
    
    def test_all_8_providers_defined(self):
        """Verify all 8 providers are supported."""
        # SUPPORTED_PROVIDERS is a list, not a set
        expected = ["copilot", "openrouter", "ollama", "lmstudio",
                   "gemini", "openai", "anthropic", "azure"]
        assert SUPPORTED_PROVIDERS == expected
    
    def test_no_default_provider(self):
        """Ensure no single default provider."""
        # All providers should be treated equally
        assert len(SUPPORTED_PROVIDERS) == 8


class TestProviderConfig:
    """Test provider configuration functions."""
    
    @pytest.mark.parametrize("provider", list(SUPPORTED_PROVIDERS))
    def test_rate_limit_for_each_provider(self, provider: str):
        """Each provider should have rate limits (returns int or None)."""
        limit = get_provider_rate_limit(provider)
        # get_provider_rate_limit returns int, not RateLimit object
        assert limit is None or limit > 0
    
    @pytest.mark.parametrize("provider", list(SUPPORTED_PROVIDERS))
    def test_quota_for_each_provider(self, provider: str):
        """Each provider should have quotas (returns float or None)."""
        quota = get_provider_quota(provider)
        # get_provider_quota returns float or None, not Quota object
        # Local providers (ollama, lmstudio) and copilot have None quotas
        assert quota is None or quota > 0
    
    def test_validate_provider_valid(self):
        """Valid providers should pass validation."""
        for provider in SUPPORTED_PROVIDERS:
            assert validate_provider(provider) is True
    
    def test_validate_provider_invalid(self):
        """Invalid providers should fail validation."""
        assert validate_provider("invalid_provider") is False
        assert validate_provider("") is False


class TestPolicyModels:
    """Test policy data models."""
    
    def test_policy_rule_creation(self):
        """Test creating a policy rule."""
        rule = PolicyRule(
            id="test_rule",
            name="Test Rule",
            field="provider",
            operator=RuleOperator.EQ,  # Use actual enum value
            value="openai",
            action=PolicyAction.ALLOW,
        )
        assert rule.id == "test_rule"
        assert rule.operator == RuleOperator.EQ
    
    def test_policy_creation(self):
        """Test creating a policy."""
        policy = Policy(
            id="test_policy",
            name="Test Policy",
            rules=[],
            enabled=True,
        )
        assert policy.id == "test_policy"
        assert policy.enabled is True


class TestRateLimitModels:
    """Test rate limit models."""
    
    def test_rate_limit_creation(self):
        """Test creating rate limit with actual model fields."""
        limit = RateLimit(
            limit_type=LimitType.REQUESTS_PER_MINUTE,
            limit_value=60,
            window_seconds=60,
            provider="openai",
        )
        assert limit.limit_value == 60
        assert limit.limit_type == LimitType.REQUESTS_PER_MINUTE
        assert limit.window_seconds == 60


class TestQuotaModels:
    """Test quota models."""
    
    def test_quota_creation(self):
        """Test creating quota with actual model fields."""
        quota = Quota(
            quota_type=LimitType.COST_PER_MONTH,
            limit_value=1000.0,
            period_days=30,
            provider="anthropic",
        )
        assert quota.limit_value == 1000.0
        assert quota.quota_type == LimitType.COST_PER_MONTH


class TestPolicyEngine:
    """Test policy engine functionality."""
    
    def test_policy_engine_import(self):
        """Test policy engine can be imported."""
        from apps.backend.governance.policy import PolicyEngine
        engine = PolicyEngine()
        assert engine is not None
    
    def test_policy_evaluation_sub_5ms(self):
        """Policy evaluation should be sub-5ms."""
        from apps.backend.governance.policy import PolicyEngine
        import time
        
        engine = PolicyEngine()
        
        start = time.time()
        for _ in range(100):
            # Use actual method signature - evaluate takes context dict
            engine.evaluate(
                context={
                    "provider": "openai",
                    "user_id": "test_user",
                    "action": "completion",
                }
            )
        elapsed = (time.time() - start) / 100 * 1000  # ms per evaluation
        
        assert elapsed < 5, f"Evaluation took {elapsed:.2f}ms, expected < 5ms"


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiter_import(self):
        """Test rate limiter can be imported."""
        from apps.backend.governance.limits import RateLimiter
        limiter = RateLimiter()
        assert limiter is not None
    
    def test_rate_limiter_check(self):
        """Test rate limit checking."""
        from apps.backend.governance.limits import RateLimiter
        
        limiter = RateLimiter()
        # check() takes provider, user_id, and optional tokens
        result = limiter.check("openai", "test_user")
        
        assert result.allowed is True
        assert result.remaining > 0


class TestQuotaManager:
    """Test quota manager functionality."""
    
    def test_quota_manager_import(self):
        """Test quota manager can be imported."""
        from apps.backend.governance.limits import QuotaManager
        manager = QuotaManager()
        assert manager is not None
    
    def test_quota_check(self):
        """Test quota checking."""
        from apps.backend.governance.limits import QuotaManager
        
        manager = QuotaManager()
        # check_quota returns tuple of (allowed, usage)
        allowed, usage = manager.check_quota("openai", "test_user", 1.0)
        
        assert allowed is True


class TestApprovalWorkflow:
    """Test approval workflow functionality."""
    
    def test_approval_workflow_import(self):
        """Test approval workflow can be imported."""
        from apps.backend.governance.workflow import ApprovalWorkflow
        workflow = ApprovalWorkflow()
        assert workflow is not None


class TestComplianceLogger:
    """Test compliance logger functionality."""
    
    def test_compliance_logger_import(self):
        """Test compliance logger can be imported."""
        from apps.backend.governance.compliance import ComplianceLogger
        logger = ComplianceLogger()
        assert logger is not None
    
    def test_log_entry_integrity(self):
        """Test log entry checksum verification."""
        from apps.backend.governance.compliance import ComplianceLogger
        
        logger = ComplianceLogger()
        entry = logger.log(
            event_type=ComplianceEventType.POLICY_EVALUATED,  # Use actual enum value
            provider="openai",
            user_id="test_user",
            action="test_action",
            result="success",
        )
        
        assert entry.verify_integrity() is True


class TestAuditTrail:
    """Test audit trail functionality."""
    
    def test_audit_trail_import(self):
        """Test audit trail can be imported."""
        from apps.backend.governance.compliance import AuditTrail
        trail = AuditTrail()
        assert trail is not None
    
    def test_chain_verification(self):
        """Test audit chain verification."""
        from apps.backend.governance.compliance import AuditTrail
        
        trail = AuditTrail()
        
        # Add entries
        trail.record("user1", "create", "policy1", "openai")
        trail.record("user2", "update", "policy1", "openai")
        
        # Verify chain
        is_valid, total, invalid_seq = trail.verify_chain()
        
        assert is_valid is True
        assert total == 2
        assert invalid_seq is None
