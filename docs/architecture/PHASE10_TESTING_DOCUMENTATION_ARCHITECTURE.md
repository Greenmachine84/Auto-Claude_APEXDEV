# Phase 10: Testing & Documentation Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 10 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Reference: `docs/specs/phase-10-testing-docs.md`

---

## Overview

Phase 10 implements comprehensive testing infrastructure and documentation generation. All testing is **LLM-Agnostic** with parametrized tests for all 8 LLM providers and 4 authentication providers.

---

## Quality Standards

| Standard | Target | Verification |
|----------|--------|-------------|
| Code Coverage | ≥90% | Coverage report |
| CI Pipeline | 100% Pass | GitHub Actions |
| Zero Flaky Tests | 10 consecutive passes | CI history |
| API Docs | 100% coverage | OpenAPI spec |

---

## LLM-Agnostic Testing Design

> **CRITICAL**: All 8 LLM providers MUST be tested equally.
> All 4 authentication providers MUST be tested.
> NO default provider - parametrized tests cover all.

### Provider Test Matrix
| Provider | Test Count | Mock Required |
|----------|------------|---------------|
| copilot | ✅ | Yes |
| openrouter | ✅ | Yes |
| ollama | ✅ | Yes |
| lmstudio | ✅ | Yes |
| gemini | ✅ | Yes |
| openai | ✅ | Yes |
| anthropic | ✅ | Yes |
| azure | ✅ | Yes |

### Auth Provider Test Matrix
| Auth Provider | Test Count |
|---------------|------------|
| github | ✅ |
| google | ✅ |
| microsoft | ✅ |
| manual | ✅ |

---

## Directory Structure

```
tests/
├── __init__.py                        # Test package init
├── conftest.py                        # Shared fixtures (all providers)
├── pytest.ini                         # Pytest configuration
│
├── unit/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_base_agent.py             # Base agent tests
│   │   ├── test_registry.py               # Agent registry tests
│   │   └── test_enterprise_agents.py      # Enterprise agent tests
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_providers.py              # Tests ALL 8 providers
│   │   ├── test_router.py                 # LLM router tests
│   │   └── test_per_agent_config.py       # Per-agent LLM config tests
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── test_oauth.py                  # Tests ALL 4 auth providers
│   │   ├── test_session.py                # Session management tests
│   │   └── test_credentials.py            # Credential vault tests
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── test_hmem.py                   # H-MEM tiered memory tests
│   │   └── test_search.py                 # Semantic search tests
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── test_scanner.py                # Secrets scanner tests
│   │   ├── test_injection.py              # Prompt injection tests
│   │   ├── test_rbac.py                   # RBAC tests
│   │   └── test_audit.py                  # Audit logging tests
│   │
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── test_task_queue.py             # TaskQueue tests
│   │   ├── test_agent_pool.py             # AgentPool tests
│   │   └── test_message_bus.py            # Message bus tests
│   │
│   ├── governance/
│   │   ├── __init__.py
│   │   ├── test_policy.py                 # Policy engine tests
│   │   ├── test_rate_limiter.py           # Per-provider rate limit tests
│   │   └── test_quota.py                  # Per-provider quota tests
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── test_cost_tracker.py           # Multi-provider cost tests
│   │   └── test_metrics.py                # Metrics collection tests
│   │
│   └── tools/
│       ├── __init__.py
│       ├── test_registry.py               # Tool registry tests
│       └── test_executor.py               # Tool executor tests
│
├── integration/
│   ├── __init__.py
│   ├── test_agent_llm_integration.py      # Agent + LLM integration
│   ├── test_auth_flow.py                  # Full auth flow tests
│   ├── test_memory_persistence.py         # Memory persistence tests
│   ├── test_orchestration_flow.py         # Orchestration flow tests
│   ├── test_provider_failover.py          # Provider failover tests
│   └── test_cost_tracking.py              # Cost tracking integration
│
├── e2e/
│   ├── __init__.py
│   ├── test_user_journey.py               # Full user journey
│   ├── test_agent_creation.py             # Agent creation e2e
│   ├── test_code_review_flow.py           # Code review flow
│   ├── test_multi_provider.py             # Multi-provider e2e
│   └── test_governance_flow.py            # Governance e2e
│
├── fixtures/
│   ├── __init__.py
│   ├── provider_fixtures.py               # All 8 provider fixtures
│   ├── auth_fixtures.py                   # All 4 auth fixtures
│   ├── agent_fixtures.py                  # Agent test fixtures
│   └── data_fixtures.py                   # Test data fixtures
│
└── mocks/
    ├── __init__.py
    ├── mock_llm_providers.py              # Mock all 8 LLM providers
    ├── mock_auth_providers.py             # Mock all 4 auth providers
    └── mock_external_services.py          # Mock external APIs

docs/
├── api/
│   ├── openapi.yaml                       # OpenAPI spec (generated)
│   ├── agents.md                          # Agent API docs
│   ├── llm.md                             # LLM API docs
│   ├── auth.md                            # Auth API docs
│   ├── memory.md                          # Memory API docs
│   ├── security.md                        # Security API docs
│   ├── governance.md                      # Governance API docs
│   └── analytics.md                       # Analytics API docs
│
├── guides/
│   ├── README.md                          # Guides index
│   ├── getting-started.md                 # Quick start guide
│   ├── llm-providers.md                   # LLM provider setup (all 8)
│   ├── authentication.md                  # Auth setup (all 4)
│   ├── agents.md                          # Agent configuration
│   ├── enterprise-agents.md               # Enterprise agent usage
│   ├── security.md                        # Security configuration
│   └── governance.md                      # Governance setup
│
├── development/
│   ├── README.md                          # Development index
│   ├── setup.md                           # Development setup
│   ├── architecture.md                    # Architecture overview
│   ├── contributing.md                    # Contribution guide
│   ├── testing.md                         # Testing guide
│   └── adding-providers.md                # Adding new LLM providers
│
└── generators/
    ├── __init__.py                        # Generator package
    ├── api_doc_generator.py               # OpenAPI generation
    ├── schema_doc_generator.py            # Schema documentation
    ├── agent_doc_generator.py             # Agent documentation
    └── provider_doc_generator.py          # Provider documentation
```

---

## File Specifications

### 1. Test Configuration

#### `conftest.py`
**Purpose**: Shared test fixtures for all providers
**Key Components**:
```python
"""Shared test fixtures for LLM-Agnostic platform."""
import pytest

# All 8 LLM providers
LLM_PROVIDERS = [
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
]

# All 4 auth providers
AUTH_PROVIDERS = ["github", "google", "microsoft", "manual"]


@pytest.fixture(params=LLM_PROVIDERS)
def llm_provider_id(request):
    """Parametrized LLM provider ID - tests all 8 providers."""
    return request.param


@pytest.fixture(params=AUTH_PROVIDERS)
def auth_provider_id(request):
    """Parametrized auth provider ID - tests all 4 providers."""
    return request.param


@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response."""
    return {
        "content": "Test response",
        "tokens": {"prompt": 10, "completion": 5},
        "model": "test-model",
    }


@pytest.fixture
def mock_provider_factory(mock_llm_response):
    """Factory for creating mock providers."""
    from unittest.mock import AsyncMock, MagicMock
    
    def create_mock(provider_id: str):
        provider = MagicMock()
        provider.complete = AsyncMock(return_value=mock_llm_response)
        provider.provider_id = provider_id
        provider.is_available = True
        return provider
    
    return create_mock


@pytest.fixture
def test_agent_config(llm_provider_id):
    """
    Test agent config with each LLM provider.
    
    Parametrized to test all 8 providers.
    """
    from apps.backend.agents.enterprise.config import (
        EnterpriseAgentConfig, AgentLLMConfig
    )
    return EnterpriseAgentConfig(
        agent_id=f"test-agent-{llm_provider_id}",
        agent_type="code_review",
        name=f"Test Agent ({llm_provider_id})",
        llm_config=AgentLLMConfig(
            provider=llm_provider_id,
            model="test-model",
        ),
    )
```

#### `pytest.ini`
**Purpose**: Pytest configuration
**Key Components**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --cov=apps --cov-report=html --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
    provider: Tests specific to LLM providers
```

---

### 2. Unit Tests

#### `unit/llm/test_providers.py`
**Purpose**: Test ALL 8 LLM providers equally
**Key Components**:
```python
@pytest.mark.parametrize("provider_id", LLM_PROVIDERS)
class TestAllProviders:
    """Test each of 8 providers equally."""
    
    async def test_provider_instantiation(self, provider_id):
        """Each provider can be created."""
        pass
    
    async def test_provider_configuration(self, provider_id):
        """Each provider can be configured."""
        pass
    
    async def test_provider_complete(self, provider_id, mock_http):
        """Each provider can complete requests."""
        pass
    
    async def test_provider_error_handling(self, provider_id):
        """Each provider handles errors correctly."""
        pass
    
    async def test_provider_timeout(self, provider_id):
        """Each provider respects timeout."""
        pass
```

#### `unit/auth/test_oauth.py`
**Purpose**: Test ALL 4 auth providers
**Key Components**:
```python
@pytest.mark.parametrize("auth_provider", AUTH_PROVIDERS)
class TestAllAuthProviders:
    """Test each of 4 auth providers."""
    
    async def test_auth_flow_initiation(self, auth_provider):
        """Each auth provider can initiate flow."""
        pass
    
    async def test_auth_callback_handling(self, auth_provider):
        """Each auth provider handles callbacks."""
        pass
    
    async def test_token_refresh(self, auth_provider):
        """Each auth provider can refresh tokens."""
        pass
```

#### `unit/llm/test_per_agent_config.py`
**Purpose**: Test per-agent LLM assignment
**Key Components**:
```python
class TestPerAgentLLMAssignment:
    """Verify agents can use different LLM providers."""
    
    async def test_multiple_agents_different_providers(self):
        """Multiple agents using different providers simultaneously."""
        pass
    
    async def test_no_default_provider_enforcement(self):
        """Agent creation without provider fails."""
        pass
    
    async def test_fallback_provider_works(self):
        """Fallback provider used on failure."""
        pass
```

---

### 3. Integration Tests

#### `integration/test_provider_failover.py`
**Purpose**: Test provider failover behavior
**Key Components**:
```python
class TestProviderFailover:
    async def test_failover_to_backup_provider(self):
        """System fails over to backup provider."""
        pass
    
    async def test_all_providers_exhausted(self):
        """Correct error when all providers fail."""
        pass
    
    @pytest.mark.parametrize("primary,backup", [
        ("openai", "anthropic"),
        ("anthropic", "gemini"),
        ("gemini", "ollama"),
    ])
    async def test_specific_failover_pairs(self, primary, backup):
        """Test specific failover combinations."""
        pass
```

---

### 4. E2E Tests

#### `e2e/test_multi_provider.py`
**Purpose**: End-to-end multi-provider tests
**Key Components**:
```python
class TestMultiProviderE2E:
    async def test_agents_use_different_providers(self):
        """Multiple agents running with different providers."""
        pass
    
    async def test_provider_switching_runtime(self):
        """Switch provider during runtime."""
        pass
    
    async def test_cost_tracking_multi_provider(self):
        """Costs tracked correctly for multiple providers."""
        pass
```

---

### 5. Fixtures

#### `fixtures/provider_fixtures.py`
**Purpose**: Fixtures for all 8 LLM providers
**Key Components**:
```python
PROVIDER_TEST_CONFIGS = {
    "copilot": {
        "mock_response": {"content": "Copilot response"},
        "test_model": "gpt-4o",
    },
    "openrouter": {
        "mock_response": {"content": "OpenRouter response"},
        "test_model": "anthropic/claude-3-sonnet",
    },
    "ollama": {
        "mock_response": {"content": "Ollama response"},
        "test_model": "llama3.2",
    },
    "lmstudio": {
        "mock_response": {"content": "LMStudio response"},
        "test_model": "local-model",
    },
    "gemini": {
        "mock_response": {"content": "Gemini response"},
        "test_model": "gemini-2.0-flash",
    },
    "openai": {
        "mock_response": {"content": "OpenAI response"},
        "test_model": "gpt-4o",
    },
    "anthropic": {
        "mock_response": {"content": "Anthropic response"},
        "test_model": "claude-sonnet-4-20250514",
    },
    "azure": {
        "mock_response": {"content": "Azure response"},
        "test_model": "gpt-4o",
    },
}
```

---

### 6. Mocks

#### `mocks/mock_llm_providers.py`
**Purpose**: Mock implementations for all 8 providers
**Key Components**:
```python
class MockLLMProvider:
    """Generic mock for any LLM provider."""
    
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self.calls = []
    
    async def complete(self, messages, **kwargs):
        self.calls.append({"messages": messages, "kwargs": kwargs})
        return PROVIDER_TEST_CONFIGS[self.provider_id]["mock_response"]


def create_mock_provider(provider_id: str) -> MockLLMProvider:
    """Factory for creating mock providers."""
    assert provider_id in PROVIDER_TEST_CONFIGS
    return MockLLMProvider(provider_id)
```

---

### 7. Documentation

#### `docs/guides/llm-providers.md`
**Purpose**: Guide for configuring all 8 LLM providers
**Key Sections**:
- Provider overview
- Configuration steps for each provider
- Per-agent assignment
- Failover configuration
- Cost optimization

#### `docs/guides/authentication.md`
**Purpose**: Guide for all 4 auth providers
**Key Sections**:
- OAuth setup (GitHub, Google, Microsoft)
- Manual authentication
- Session management
- Security best practices

#### `docs/development/adding-providers.md`
**Purpose**: Guide for adding new LLM providers
**Key Sections**:
- Provider interface
- Implementation requirements
- Testing requirements
- Documentation requirements

---

### 8. Documentation Generators

#### `generators/api_doc_generator.py`
**Purpose**: Generate OpenAPI spec from code
**Key Components**:
```python
class APIDocGenerator:
    def generate_openapi(self, app) -> dict
    def write_spec(self, path: str) -> None
    def generate_markdown(self, spec: dict) -> str
```

#### `generators/provider_doc_generator.py`
**Purpose**: Generate provider documentation
**Key Components**:
```python
class ProviderDocGenerator:
    def generate_provider_docs(self) -> str
    def generate_model_matrix(self) -> str
    def generate_pricing_table(self) -> str
```

---

## Test Coverage Targets

| Module | Target | Minimum |
|--------|--------|--------|
| LLM Providers | 95% | 90% |
| Authentication | 95% | 90% |
| Security | 98% | 95% |
| Governance | 95% | 90% |
| Agents | 90% | 85% |
| Overall | 92% | 90% |

---

## Integration Points

### With All Phases
- Unit tests for each phase's components
- Integration tests for cross-phase functionality
- E2E tests for complete workflows

### With CI/CD
- GitHub Actions integration
- Coverage reporting
- Test result publishing

---

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Unit test time | <2 min | >5 min |
| Integration test time | <5 min | >10 min |
| E2E test time | <10 min | >20 min |
| Doc build time | <1 min | >3 min |
| Coverage report time | <30s | >60s |

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `tests/` (core) | 3 | Test configuration |
| `tests/unit/agents/` | 4 | Agent unit tests |
| `tests/unit/llm/` | 4 | LLM provider tests |
| `tests/unit/auth/` | 4 | Auth provider tests |
| `tests/unit/memory/` | 3 | Memory tests |
| `tests/unit/security/` | 5 | Security tests |
| `tests/unit/orchestration/` | 4 | Orchestration tests |
| `tests/unit/governance/` | 4 | Governance tests |
| `tests/unit/analytics/` | 3 | Analytics tests |
| `tests/unit/tools/` | 3 | Tools tests |
| `tests/integration/` | 7 | Integration tests |
| `tests/e2e/` | 6 | E2E tests |
| `tests/fixtures/` | 5 | Test fixtures |
| `tests/mocks/` | 4 | Mock providers |
| `docs/api/` | 8 | API documentation |
| `docs/guides/` | 8 | User guides |
| `docs/development/` | 6 | Developer docs |
| `docs/generators/` | 5 | Doc generators |
| **Total** | **86** | Phase 10 files |

---

## Completion Summary

### Phase 10 Deliverables
- 59 test files covering all components
- 22 documentation files
- 5 documentation generators
- Parametrized tests for all 8 LLM providers
- Parametrized tests for all 4 auth providers
- 90%+ code coverage target

---

*Phase 10 Architecture complete. 86 files specified for testing and documentation.*

---

## PHASES 6-10 ARCHITECTURE COMPLETE

All 5 missing phases have been specified:

| Phase | Files | Focus |
|-------|-------|-------|
| Phase 6 | 28 | Security |
| Phase 7 | 39 | Enterprise Agents |
| Phase 8 | 41 | Analytics & Tools |
| Phase 9 | 24 | Governance |
| Phase 10 | 86 | Testing & Documentation |
| **Total** | **218** | Phases 6-10 |
