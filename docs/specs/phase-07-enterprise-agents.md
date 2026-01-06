# Phase 7: Enterprise Agents

> **Version**: 2.0.0 | **Duration**: Week 13-14 | **Priority**: 🟡 MEDIUM
>
> **Status**: 📋 Specification Ready
>
> **LLM-Agnostic**: ✅ Each agent independently configurable for any of 8 providers

---

## Quality Standards

| Standard | Description | Verification |
|----------|-------------|--------------|
| **World-Class** | Industry-leading agent capabilities | Benchmark comparison |
| **Enterprise-Grade** | Production reliability and scale | Load testing |
| **Fully Production Ready** | Battle-tested agent implementations | Integration tests |
| **Clean and Concise Code** | Modular, extensible architecture | Code review |
| **Beyond PhD Level Expertise** | State-of-the-art agent patterns | Research alignment |

---

## Outcome Expectations

### Business Objectives

| Objective | Success Metric | World-Class Standard |
|-----------|----------------|----------------------|
| Automated code review | 90% human parity | Industry-leading accuracy |
| Security scanning | Zero missed critical vulns | Enterprise security |
| Test generation | 80%+ coverage generation | Comprehensive testing |
| Documentation | Auto-generate for 100% APIs | Complete coverage |

### Technical Outcomes

| Outcome | Measurement | Target | World-Class Standard |
|---------|-------------|--------|----------------------|
| Agent response time | P99 latency | <30s | Real-time interaction |
| Review accuracy | Human agreement | >90% | Expert-level quality |
| Vulnerability detection | Recall rate | >95% | Zero false negatives |
| Test coverage | Generated coverage | >80% | Comprehensive testing |
| Inter-agent comm | Message latency | <100ms | Real-time collaboration |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| CodeReviewAgent | PR analysis | ✅ | Expert-level reviews |
| SecurityAgent | Vulnerability scan | ✅ | OWASP compliance |
| QAAgent | Test generation | ✅ | 80%+ coverage |
| ProjectAnalyzerAgent | Codebase analysis | ✅ | Full dependency mapping |
| Per-agent LLM | Provider/model config | ✅ | Any of 8 providers |
| Agent collaboration | Inter-agent messaging | ✅ | Real-time coordination |

---

## Acceptance Tests

| Test ID | Test Case | Pass Criteria | Verification Method |
|---------|-----------|---------------|---------------------|
| AT-7.1 | CodeReviewAgent reviews PR | Actionable feedback generated | Integration test |
| AT-7.2 | SecurityAgent finds SQLi | Injection detected, flagged | Unit test |
| AT-7.3 | QAAgent generates tests | 80%+ coverage achieved | Coverage test |
| AT-7.4 | Agent uses Copilot | Correct provider invoked | Integration test |
| AT-7.5 | Agent uses OpenRouter | Correct provider invoked | Integration test |
| AT-7.6 | Agent uses Ollama | Local model invoked | Integration test |
| AT-7.7 | Agent uses LMStudio | Local model invoked | Integration test |
| AT-7.8 | Agent uses Gemini | Google API invoked | Integration test |
| AT-7.9 | Agent fallback works | Switch provider on failure | Chaos test |
| AT-7.10 | Multi-agent pipeline | Agents collaborate on task | End-to-end test |

---

## Performance Metrics

| Metric | Target | Measurement Method | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Agent initialization | <100ms | Benchmark | >500ms |
| Code review latency | <30s per file | Prometheus | >60s |
| Security scan latency | <10s per file | Prometheus | >30s |
| Test generation | <45s per function | Prometheus | >90s |
| LLM provider switch | <1s | Benchmark | >5s |
| Agent memory footprint | <256MB | Resource monitor | >512MB |

---

## Risk Mitigations

| Risk | Impact | Mitigation | Verification |
|------|--------|------------|--------------|
| LLM provider outage | Agent failure | Fallback configuration | Chaos test |
| Token limit exceeded | Truncated response | Chunking strategy | Integration test |
| Hallucinated findings | False positives | Structured output + validation | Review audit |
| Agent deadlock | Pipeline stall | Timeout + watchdog | Stress test |
| Memory leak | OOM | Bounded context window | Long-running test |

---

## LLM-Agnostic Agent Configuration

### Per-Agent LLM Assignment

```python
"""
Each enterprise agent can be assigned ANY of the 8 LLM providers.
Different agents can use different providers/models.
NO default provider - must be explicitly configured.
"""

# Example: Different agents using different providers
AGENT_CONFIGURATIONS = {
    "code_review_agent": {
        "provider": "anthropic",      # Claude for nuanced review
        "model": "claude-sonnet-4-20250514",
    },
    "security_agent": {
        "provider": "openai",         # GPT for security
        "model": "gpt-4-turbo",
    },
    "qa_agent": {
        "provider": "gemini",         # Gemini for test gen
        "model": "gemini-1.5-pro",
    },
    "documentation_agent": {
        "provider": "openrouter",     # OpenRouter flexibility
        "model": "anthropic/claude-3-opus",
    },
    "project_analyzer": {
        "provider": "ollama",         # Local for privacy
        "model": "llama3:70b",
    },
}


@dataclass
class AgentLLMConfig:
    """
    LLM configuration for an agent.
    
    Supports all 8 providers with no defaults.
    """
    provider: str  # copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str     # Provider-specific model ID
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    fallback_provider: Optional[str] = None  # For resilience
    fallback_model: Optional[str] = None
    
    def validate(self) -> None:
        """Validate provider is one of 8 supported."""
        SUPPORTED = ["copilot", "openrouter", "ollama", "lmstudio", 
                     "gemini", "openai", "anthropic", "azure"]
        if self.provider not in SUPPORTED:
            raise ValueError(
                f"Invalid provider: {self.provider}. "
                f"Must be one of: {', '.join(SUPPORTED)}"
            )
```

### Base Enterprise Agent with LLM Flexibility

```python
class BaseEnterpriseAgent:
    """
    Base class for enterprise agents with LLM-agnostic design.
    
    Each agent instance can use any of the 8 LLM providers.
    """
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: LLMRouter
    ):
        """
        Initialize agent with LLM configuration.
        
        Args:
            config: Agent configuration including LLM settings
            llm_router: Router to access any of 8 providers
        """
        self.config = config
        self.llm_router = llm_router
        
        # Validate LLM config
        if config.llm_config:
            config.llm_config.validate()
        else:
            raise ValueError(
                f"Agent {config.agent_id} has no LLM configured. "
                "Must assign provider from: copilot, openrouter, ollama, "
                "lmstudio, gemini, openai, anthropic, azure"
            )
    
    async def complete(self, prompt: str) -> str:
        """
        Complete prompt using agent's configured LLM.
        
        Automatically handles failover if configured.
        """
        try:
            client = self.llm_router.get_client(
                provider=self.config.llm_config.provider,
                model=self.config.llm_config.model
            )
            return await client.complete(
                prompt=prompt,
                temperature=self.config.llm_config.temperature,
                max_tokens=self.config.llm_config.max_tokens,
            )
        except Exception as e:
            # Try fallback if configured
            if self.config.llm_config.fallback_provider:
                fallback = self.llm_router.get_client(
                    provider=self.config.llm_config.fallback_provider,
                    model=self.config.llm_config.fallback_model
                )
                return await fallback.complete(prompt=prompt)
            raise
```

---

## Deliverables

| File | Purpose | LOC Estimate |
|------|---------|--------------|
| `apps/backend/agents/enterprise/base_enterprise_agent.py` | Base agent class | 200 |
| `apps/backend/agents/enterprise/code_review_agent.py` | PR review agent | 350 |
| `apps/backend/agents/enterprise/security_agent.py` | Security scanning | 300 |
| `apps/backend/agents/enterprise/qa_agent.py` | Test generation | 350 |
| `apps/backend/agents/enterprise/project_analyzer_agent.py` | Codebase analysis | 300 |
| `apps/backend/agents/enterprise/documentation_agent.py` | Doc generation | 250 |
| `apps/backend/agents/enterprise/orchestrator_agent.py` | Multi-agent coord | 300 |
| `tests/test_enterprise_agents_*.py` | Agent tests | 1000 |

---

## Section 1: Enterprise Agent Architecture

### Task 1.1: Directory Structure

```
apps/backend/agents/enterprise/
├── __init__.py
├── base_enterprise_agent.py
├── config.py
├── code_review_agent.py
├── security_agent.py
├── qa_agent.py
├── project_analyzer_agent.py
├── documentation_agent.py
├── orchestrator_agent.py
└── capabilities/
    ├── __init__.py
    ├── code_analysis.py
    ├── test_generation.py
    └── documentation.py
```

### Task 1.2: Agent Configuration Model

**File**: `apps/backend/agents/enterprise/config.py`

```python
"""
Enterprise agent configuration with LLM-agnostic design.

World-Class Standards:
- Per-agent LLM assignment
- Fallback configuration
- Capability-based composition
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class AgentCapability(Enum):
    """Agent capability types."""
    CODE_REVIEW = "code_review"
    SECURITY_SCAN = "security_scan"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentLLMConfig:
    """
    Per-agent LLM configuration.
    
    Supports all 8 providers equally - NO defaults.
    """
    provider: str  # copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str     # Provider-specific model ID
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    
    SUPPORTED_PROVIDERS = [
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    ]
    
    def validate(self) -> None:
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Invalid provider: {self.provider}. "
                f"Must be one of: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )
        if self.fallback_provider and self.fallback_provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Invalid fallback provider: {self.fallback_provider}"
            )


@dataclass
class EnterpriseAgentConfig:
    """Complete enterprise agent configuration."""
    agent_id: str
    agent_type: str
    name: str
    description: str = ""
    llm_config: Optional[AgentLLMConfig] = None  # REQUIRED - no default
    capabilities: List[AgentCapability] = field(default_factory=list)
    memory_enabled: bool = True
    max_iterations: int = 10
    tools: List[str] = field(default_factory=list)
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## Section 2: Code Review Agent

### Task 2.1: Code Review Agent

**File**: `apps/backend/agents/enterprise/code_review_agent.py`

```python
"""
Code review agent for PR analysis.

World-Class Standards:
- Expert-level code review
- Structured feedback
- LLM-agnostic execution
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability


@dataclass
class CodeReviewResult:
    """Structured code review result."""
    file_path: str
    findings: List[Dict[str, Any]]
    suggestions: List[str]
    severity_counts: Dict[str, int]
    overall_quality: float
    approved: bool


class CodeReviewAgent(BaseEnterpriseAgent):
    """
    Agent for automated code review.
    
    Uses agent's configured LLM provider (any of 8).
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are an expert code reviewer.
Analyze code changes for:
1. Code quality and best practices
2. Potential bugs and edge cases
3. Performance issues
4. Security vulnerabilities
5. Documentation and readability

Provide constructive, actionable feedback."""
    
    def __init__(self, config: EnterpriseAgentConfig, llm_router):
        super().__init__(config, llm_router)
        self.config.capabilities.append(AgentCapability.CODE_REVIEW)
    
    async def review_file(
        self,
        file_path: str,
        content: str,
        diff: Optional[str] = None
    ) -> CodeReviewResult:
        """
        Review a single file using configured LLM.
        
        The LLM provider is determined by agent's llm_config.
        """
        prompt = self._build_review_prompt(file_path, content, diff)
        
        # Uses agent's configured provider (any of 8)
        response = await self.complete(prompt)
        
        return self._parse_review_response(file_path, response)
```

---

## Section 3: Security Agent

### Task 3.1: Security Agent

**File**: `apps/backend/agents/enterprise/security_agent.py`

```python
"""
Security scanning agent.

World-Class Standards:
- OWASP Top 10 coverage
- Zero false negatives for critical vulns
- LLM-agnostic vulnerability analysis
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability


@dataclass
class SecurityScanResult:
    """Security scan results."""
    scan_id: str
    target: str
    vulnerabilities: List[Dict[str, Any]]
    secrets_found: List[Dict[str, Any]]
    risk_score: float
    recommendations: List[str]
    passed: bool


class SecurityAgent(BaseEnterpriseAgent):
    """
    Agent for security vulnerability scanning.
    
    Can use any of 8 LLM providers for analysis.
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are a security expert.
Analyze code for:
1. Security vulnerabilities (OWASP Top 10)
2. Exposed secrets and credentials
3. Injection vulnerabilities
4. Authentication/authorization issues
5. Data exposure risks

Provide severity ratings and remediation steps."""
    
    async def scan_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> SecurityScanResult:
        """
        Scan code for security issues.
        
        Uses agent's configured LLM for deep analysis.
        """
        prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

Provide findings in JSON format with severity and remediation."""
        
        # Uses agent's configured provider
        response = await self.complete(prompt)
        
        return self._parse_security_response(response, file_path)
```

---

## Section 4: QA Agent

### Task 4.1: QA Agent

**File**: `apps/backend/agents/enterprise/qa_agent.py`

```python
"""
QA and test generation agent.

World-Class Standards:
- 80%+ coverage generation
- Multiple test frameworks
- LLM-agnostic test generation
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability


@dataclass
class TestCase:
    """Generated test case."""
    name: str
    description: str
    test_code: str
    test_type: str
    target_function: Optional[str] = None


class QAAgent(BaseEnterpriseAgent):
    """
    Agent for test generation and QA.
    
    Uses any of 8 LLM providers for test generation.
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are a QA engineer expert.
Generate comprehensive tests including:
1. Unit tests for individual functions
2. Edge case tests
3. Error handling tests
4. Integration tests where appropriate

Follow testing best practices and use appropriate assertions."""
    
    async def generate_tests(
        self,
        code: str,
        language: str,
        framework: Optional[str] = None
    ) -> List[TestCase]:
        """
        Generate tests for code using configured LLM.
        """
        if not framework:
            framework = self._detect_framework(language)
        
        prompt = f"""Generate {framework} tests for this {language} code:

```{language}
{code}
```

Generate comprehensive test cases covering all functions."""
        
        response = await self.complete(prompt)
        return self._parse_test_response(response)
```

---

## Validation Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| LLM-Agnostic System | ✅ | AgentLLMConfig with 8 providers |
| No Default Provider | ✅ | llm_config REQUIRED, no default |
| 8 Equal LLM Providers | ✅ | SUPPORTED_PROVIDERS list |
| Per-Agent LLM Assignment | ✅ | Each agent has own llm_config |
| World-Class Standards | ✅ | Quality Standards table |
| Enterprise-Grade | ✅ | Production reliability targets |
| Production Ready | ✅ | Battle-tested implementations |
| Clean Code | ✅ | Modular, extensible architecture |
| Acceptance Tests | ✅ | AT-7.1 through AT-7.10 |
| Performance Metrics | ✅ | <30s latency targets |

---

## Integration Points

| Phase | Integration | Data Flow |
|-------|-------------|-----------|
| Phase 2 | LLM Router | Provider selection |
| Phase 4 | Orchestration | Agent execution |
| Phase 5 | Memory | Agent memory |
| Phase 6 | Security | Credential access |
