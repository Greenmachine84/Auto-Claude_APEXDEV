"""
Phase 9 Governance Tests.

Comprehensive tests for the governance module.
"""

import pytest
from datetime import datetime, timedelta

# Import governance components
from apps.backend.governance.models import (
    PolicyAction, ApprovalStatus, RuleOperator,
    PolicyRule, Policy, RateLimit, Quota,
    SUPPORTED_PROVIDERS
)
from apps.backend.governance.config import (
    get_provider_rate_limit, get_provider_quota,
    is_approval_required, validate_provider
)


class TestSupportedProviders:
    """Test provider configuration."""
    
    def test_all_8_providers_defined(self):
        """Verify all 8 providers are supported."""
        expected = {"copilot", "openrouter", "ollama", "lmstudio",
                   "gemini", "openai", "anthropic", "azure"}
        assert SUPPORTED_PROVIDERS == expected
    
    def test_no_default_provider(self):
        """Ensure no single default provider."""
        # All providers should be treated equally
        assert len(SUPPORTED_PROVIDERS) == 8


class TestProviderConfig:
    """Test provider configuration functions."""
    
    @pytest.mark.parametrize("provider", list(SUPPORTED_PROVIDERS))
    def test_rate_limit_for_each_provider(self, provider: str):
        """Each provider should have rate limits."""
        limit = get_provider_rate_limit(provider)
        assert limit is not None
        assert limit.requests_per_minute > 0
    
    @pytest.mark.parametrize("provider", list(SUPPORTED_PROVIDERS))
    def test_quota_for_each_provider(self, provider: str):
        """Each provider should have quotas."""
        quota = get_provider_quota(provider)
        assert quota is not None
        assert quota.monthly_cost_limit > 0
    
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
            field="provider",
            operator=RuleOperator.EQUALS,
            value="openai",
            action=PolicyAction.ALLOW,
        )
        assert rule.id == "test_rule"
        assert rule.operator == RuleOperator.EQUALS
    
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
        """Test creating rate limit."""
        limit = RateLimit(
            provider="openai",
            requests_per_minute=60,
            tokens_per_minute=10000,
        )
        assert limit.requests_per_minute == 60
        assert limit.tokens_per_minute == 10000


class TestQuotaModels:
    """Test quota models."""
    
    def test_quota_creation(self):
        """Test creating quota."""
        quota = Quota(
            provider="anthropic",
            monthly_cost_limit=1000.0,
            daily_cost_limit=50.0,
        )
        assert quota.monthly_cost_limit == 1000.0
        assert quota.daily_cost_limit == 50.0


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
            engine.evaluate(
                provider="openai",
                user_id="test_user",
                action="completion",
                context={}
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
        from apps.backend.governance.models import ComplianceEventType
        
        logger = ComplianceLogger()
        entry = logger.log(
            event_type=ComplianceEventType.POLICY_EVALUATION,
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
