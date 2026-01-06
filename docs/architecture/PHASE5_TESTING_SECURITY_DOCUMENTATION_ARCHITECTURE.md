# Phase 5: Testing & Documentation Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 5 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Last Updated: January 2025

---

## Overview

Phase 5 establishes comprehensive **testing infrastructure** and **documentation system**. This includes unit/integration/e2e tests, test fixtures, and automated documentation generation.

> **Note**: Security implementation is defined in **[Phase 6: Security Architecture](./PHASE6_SECURITY_ARCHITECTURE.md)**. This phase covers testing for security components and security documentation structure.

---

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                        # Pytest configuration
├── pytest.ini                         # Pytest settings
│
├── unit/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_base_agent.py         # Base agent tests
│   │   ├── test_coder_agent.py        # Coder agent tests
│   │   ├── test_reviewer_agent.py     # Reviewer tests
│   │   ├── test_fixer_agent.py        # Fixer tests
│   │   ├── test_agent_registry.py     # Registry tests
│   │   ├── test_agent_factory.py      # Factory tests
│   │   └── test_agent_lifecycle.py    # Lifecycle tests
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── test_episode_store.py      # Episode storage tests
│   │   ├── test_episode_query.py      # Query builder tests
│   │   ├── test_semantic_search.py    # Semantic search tests
│   │   ├── test_hmem_tiers.py         # H-MEM tier tests
│   │   └── test_context_builder.py    # Context builder tests
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_llm_client.py         # LLM client tests
│   │   ├── test_llm_router.py         # Router tests
│   │   ├── test_model_selector.py     # Model selection tests
│   │   ├── test_prompt_template.py    # Template tests
│   │   └── test_tool_executor.py      # Tool execution tests
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── test_skill_registry.py     # Skill registry tests
│   │   ├── test_skill_executor.py     # Executor tests
│   │   ├── test_coding_skills.py      # Coding skill tests
│   │   └── test_review_skills.py      # Review skill tests
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── test_tool_registry.py      # Tool registry tests
│   │   ├── test_tool_permissions.py   # Permission tests
│   │   ├── test_tool_sandbox.py       # Sandbox tests
│   │   ├── test_filesystem_tools.py   # FS tool tests
│   │   └── test_git_tools.py          # Git tool tests
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── test_task_queue.py         # Queue tests
│   │   ├── test_agent_pool.py         # Pool tests
│   │   ├── test_workflow_engine.py    # Workflow tests
│   │   ├── test_dispatcher.py         # Dispatcher tests
│   │   └── test_result_collector.py   # Result tests
│   │
│   └── security/                      # Tests for Phase 6 security module
│       ├── __init__.py
│       ├── test_secrets_scanner.py    # Secret detection tests
│       ├── test_prompt_injection.py   # Injection guard tests
│       ├── test_credential_vault.py   # Vault tests
│       ├── test_audit_logger.py       # Audit tests
│       ├── test_rbac.py               # RBAC tests
│       └── test_input_validation.py   # Validation tests
│
├── integration/
│   ├── __init__.py
│   │
│   ├── test_agent_memory.py           # Agent + Memory integration
│   ├── test_agent_llm.py              # Agent + LLM integration
│   ├── test_orchestrator_agents.py    # Orchestrator + Agents
│   ├── test_workflow_execution.py     # Full workflow execution
│   ├── test_skill_tool_chain.py       # Skill + Tool chain
│   ├── test_memory_persistence.py     # Memory persistence
│   ├── test_ipc_communication.py      # IPC integration
│   └── test_security_integration.py   # Security module integration
│
├── e2e/
│   ├── __init__.py
│   │
│   ├── test_task_lifecycle.py         # Full task lifecycle
│   ├── test_code_generation_flow.py   # Code gen end-to-end
│   ├── test_review_fix_cycle.py       # Review-fix cycle
│   ├── test_multi_agent_workflow.py   # Multi-agent coordination
│   └── test_external_integrations.py  # GitHub/GitLab/etc.
│
├── fixtures/
│   ├── __init__.py
│   ├── agent_fixtures.py              # Agent test fixtures
│   ├── task_fixtures.py               # Task test fixtures
│   ├── memory_fixtures.py             # Memory test fixtures
│   ├── llm_fixtures.py                # LLM mock fixtures
│   ├── security_fixtures.py           # Security test fixtures
│   └── sample_code_fixtures.py        # Sample code for tests
│
└── mocks/
    ├── __init__.py
    ├── mock_llm_client.py             # Mock LLM responses
    ├── mock_memory_store.py           # Mock memory
    ├── mock_tool_executor.py          # Mock tool execution
    └── mock_external_apis.py          # Mock GitHub/GitLab

apps/
└── backend/
    └── documentation/
        ├── __init__.py                    # Doc exports
        │
        ├── generators/
        │   ├── __init__.py                # Generator exports
        │   ├── api_doc_generator.py       # API documentation
        │   ├── schema_doc_generator.py    # Schema documentation
        │   ├── agent_doc_generator.py     # Agent documentation
        │   ├── tool_doc_generator.py      # Tool documentation
        │   └── skill_doc_generator.py     # Skill documentation
        │
        ├── templates/
        │   ├── __init__.py                # Template exports
        │   ├── markdown_template.py       # Markdown generator
        │   ├── html_template.py           # HTML generator
        │   └── openapi_template.py        # OpenAPI spec generator
        │
        ├── builders/
        │   ├── __init__.py                # Builder exports
        │   ├── readme_builder.py          # README generation
        │   ├── changelog_builder.py       # Changelog generation
        │   ├── decision_builder.py        # ADR generation
        │   └── user_guide_builder.py      # User guide generation
        │
        └── types/
            ├── __init__.py                # Type exports
            ├── doc_types.py               # Documentation types
            └── template_types.py          # Template types

docs/
├── api/
│   ├── README.md                      # API docs index
│   ├── agents-api.md                  # Agent API reference
│   ├── memory-api.md                  # Memory API reference
│   ├── llm-api.md                     # LLM API reference
│   ├── tools-api.md                   # Tools API reference
│   ├── skills-api.md                  # Skills API reference
│   ├── orchestrator-api.md            # Orchestrator API reference
│   └── integrations-api.md            # Integrations API reference
│
├── guides/
│   ├── README.md                      # Guides index
│   ├── getting-started.md             # Quick start guide
│   ├── installation.md                # Installation guide
│   ├── configuration.md               # Configuration guide
│   ├── creating-tasks.md              # Task creation guide
│   ├── using-agents.md                # Agent usage guide
│   ├── custom-workflows.md            # Workflow customization
│   ├── integrations-setup.md          # Integration setup
│   └── troubleshooting.md             # Troubleshooting guide
│
├── architecture/
│   ├── README.md                      # Architecture overview
│   ├── PHASE1_*.md through PHASE10_*.md
│   └── (this file)
│
├── security/                          # Security documentation
│   ├── README.md                      # Security overview
│   ├── security-model.md              # Security model
│   ├── authentication.md              # Auth documentation
│   ├── authorization.md               # Authorization model
│   ├── audit-logging.md               # Audit log documentation
│   └── prompt-injection-defense.md    # Prompt injection defense
│
└── development/
    ├── README.md                      # Development overview
    ├── contributing.md                # Contribution guide
    ├── coding-standards.md            # Coding standards
    ├── testing-guide.md               # Testing guide
    ├── release-process.md             # Release process
    └── architecture-decisions.md      # ADR guide
```

---

## Security Implementation Reference

> **⚠️ IMPORTANT**: The security module implementation (`apps/backend/security/`) is fully specified in **[Phase 6: Security Architecture](./PHASE6_SECURITY_ARCHITECTURE.md)**.

Phase 6 defines:
- **Scanner Module**: Secrets detection, prompt injection defense, code scanning
- **Encryption Module**: Credential vault, key management, AES-256-GCM
- **Audit Module**: Immutable logging, integrity verification
- **RBAC Module**: Role management, permission enforcement
- **Validation Module**: Input/output validation, threat detection

This phase (Phase 5) covers:
- **Security Tests**: Unit and integration tests for Phase 6 components
- **Security Documentation**: User-facing security guides in `docs/security/`

---

## File Specifications

### 1. Test Infrastructure

#### `conftest.py`
**Purpose**: Pytest configuration and shared fixtures
**Key Components**:
```python
# Shared fixtures available to all tests
@pytest.fixture
def mock_llm_client() -> MockLLMClient

@pytest.fixture
def memory_store() -> EpisodeStore

@pytest.fixture
def agent_factory() -> AgentFactory

@pytest.fixture
def task_queue() -> TaskQueue

@pytest.fixture
def security_context() -> SecurityContext  # From Phase 6
```

#### Unit Tests Structure

| Domain | Test Files | Coverage Target |
|--------|------------|----------------|
| Agents | 7 | Base, Core (4), Registry, Factory, Lifecycle |
| Memory | 5 | Store, Query, Semantic, H-MEM, Context |
| LLM | 5 | Client, Router, Selector, Template, Tools |
| Skills | 4 | Registry, Executor, Coding, Review |
| Tools | 5 | Registry, Permissions, Sandbox, FS, Git |
| Orchestrator | 5 | Queue, Pool, Workflow, Dispatch, Results |
| Security | 6 | Scanner, Injection, Vault, Audit, RBAC, Validation |

#### Integration Tests

| Test File | Integration Points | Purpose |
|-----------|-------------------|--------|
| `test_agent_memory.py` | Agent + Memory | Episode storage on agent run |
| `test_agent_llm.py` | Agent + LLM | LLM calls from agents |
| `test_orchestrator_agents.py` | Orchestrator + Pool | Task dispatch to agents |
| `test_workflow_execution.py` | All | Complete workflow flow |
| `test_skill_tool_chain.py` | Skills + Tools | Skill using tools |
| `test_memory_persistence.py` | Memory + SQLite | Data persistence |
| `test_ipc_communication.py` | Electron + Backend | IPC message flow |
| `test_security_integration.py` | Security + All | Security across components |

#### E2E Tests

| Test File | Scenario | Duration |
|-----------|----------|----------|
| `test_task_lifecycle.py` | Create → Execute → Complete | ~30s |
| `test_code_generation_flow.py` | Spec → Generate → Review | ~60s |
| `test_review_fix_cycle.py` | Code → Review → Fix → Verify | ~120s |
| `test_multi_agent_workflow.py` | MDA orchestration | ~180s |
| `test_external_integrations.py` | GitHub PR flow | ~60s |

---

### 2. Documentation Module (`documentation/`)

#### Documentation Generators (`documentation/generators/`)

| File | Generates | Output Format |
|------|-----------|---------------|
| `api_doc_generator.py` | API reference | Markdown, HTML |
| `schema_doc_generator.py` | Data models | Markdown |
| `agent_doc_generator.py` | Agent docs | Markdown |
| `tool_doc_generator.py` | Tool reference | Markdown |
| `skill_doc_generator.py` | Skill reference | Markdown |

**API Doc Generator**:
```python
class APIDocGenerator:
    def generate_from_module(self, module: ModuleType) -> str
    def generate_from_class(self, cls: Type) -> str
    def generate_from_function(self, func: Callable) -> str
    def generate_openapi_spec(self) -> dict
```

#### Templates (`documentation/templates/`)

| File | Template Type | Features |
|------|---------------|----------|
| `markdown_template.py` | Markdown | TOC, code blocks, tables |
| `html_template.py` | HTML | Styled, searchable |
| `openapi_template.py` | OpenAPI 3.0 | Full spec generation |

#### Documentation Builders (`documentation/builders/`)

| File | Builds | Content |
|------|--------|--------|
| `readme_builder.py` | README.md | Project overview |
| `changelog_builder.py` | CHANGELOG.md | Version history |
| `decision_builder.py` | ADRs | Architecture decisions |
| `user_guide_builder.py` | User guides | How-to documentation |

---

### 3. Documentation Files (`docs/`)

#### API Documentation (`docs/api/`)

| File | Content |
|------|--------|
| `agents-api.md` | Agent classes, methods, examples |
| `memory-api.md` | Memory store, search, context APIs |
| `llm-api.md` | LLM client, providers, prompts |
| `tools-api.md` | Tool definitions, execution |
| `skills-api.md` | Skill registry, execution |
| `orchestrator-api.md` | Queue, pool, workflow APIs |
| `integrations-api.md` | GitHub, GitLab, Linear APIs |

#### User Guides (`docs/guides/`)

| File | Content |
|------|--------|
| `getting-started.md` | Quick start (15 min) |
| `installation.md` | Detailed installation |
| `configuration.md` | Config options, env vars |
| `creating-tasks.md` | Task creation, priority |
| `using-agents.md` | Agent selection, monitoring |
| `custom-workflows.md` | Workflow DSL, templates |
| `integrations-setup.md` | External integrations |
| `troubleshooting.md` | Common issues, solutions |

#### Security Documentation (`docs/security/`)

> See [Phase 6](./PHASE6_SECURITY_ARCHITECTURE.md) for implementation details.

| File | Content |
|------|--------|
| `security-model.md` | Security architecture overview |
| `authentication.md` | Auth methods, tokens |
| `authorization.md` | Permissions, roles (RBAC) |
| `audit-logging.md` | Audit trail, compliance |
| `prompt-injection-defense.md` | Injection prevention |

#### Development Documentation (`docs/development/`)

| File | Content |
|------|--------|
| `contributing.md` | How to contribute |
| `coding-standards.md` | Style guide, linting |
| `testing-guide.md` | Test writing guide |
| `release-process.md` | Release workflow |
| `architecture-decisions.md` | ADR process |

---

## Test Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|----------------|
| Agents (core) | 85% | 95% |
| Memory | 80% | 90% |
| LLM | 75% | 85% |
| Skills | 80% | 90% |
| Tools | 85% | 95% |
| Orchestrator | 80% | 90% |
| Security (Phase 6) | 90% | 98% |
| **Overall** | **80%** | **90%** |

---

## CI/CD Integration

### Test Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run unit tests
        run: pytest tests/unit --cov=apps/backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - name: Run integration tests
        run: pytest tests/integration -v

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - name: Run e2e tests
        run: pytest tests/e2e -v --timeout=300

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run security tests
        run: pytest tests/unit/security -v --strict-markers
```

### Documentation Pipeline
```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths: ['docs/**', 'apps/backend/**']

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Generate API docs
        run: python -m documentation.generators.api_doc_generator
      - name: Build site
        run: mkdocs build
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
```

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `tests/` (all) | 45+ | Unit, integration, e2e tests |
| `apps/backend/documentation/` | 15 | Doc generators |
| `docs/` (markdown) | 25+ | User documentation |
| **Total** | **85+** | Phase 5 files |

---

## Cross-Reference

| Phase | Relationship |
|-------|-------------|
| **Phase 1** | Tests for agent system |
| **Phase 2** | Tests for memory/LLM |
| **Phase 3** | Tests for skills/tools |
| **Phase 4** | Tests for UI/integrations |
| **Phase 6** | Security implementation (referenced) |
| **Phase 7** | Tests for enterprise agents |
| **Phase 9** | Tests for governance |
| **Phase 10** | Additional testing patterns |

---

## Next Steps

→ Phase 6: Security Architecture (implementation details)
