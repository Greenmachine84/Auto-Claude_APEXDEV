# Phase 7: Enterprise Agents Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 7 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Reference: `docs/specs/phase-07-enterprise-agents.md`

---

## Overview

Phase 7 implements enterprise-grade agents for automated code review, security scanning, test generation, and project analysis. Each enterprise agent is **LLM-Agnostic** and can be independently configured to use any of the 8 supported LLM providers.

---

## Quality Standards

| Standard | Target | Verification |
|----------|--------|-------------|
| Expert-Level Reviews | 90% human parity | Benchmark comparison |
| Zero False Negatives | Critical vulns | Security audit |
| 80%+ Test Generation | Coverage | Automated tests |
| Real-time Collaboration | <100ms latency | Load testing |

---

## LLM-Agnostic Design Principle

> **CRITICAL**: Each enterprise agent can use ANY of the 8 supported LLM providers.
> Different agents can use different providers simultaneously.
> NO default provider - all must be explicitly configured.

### Supported Providers
| Provider | Use Case Example |
|----------|------------------|
| copilot | IDE integration |
| openrouter | Multi-model access |
| ollama | Local/private |
| lmstudio | Local development |
| gemini | Google ecosystem |
| openai | GPT models |
| anthropic | Claude models |
| azure | Enterprise Azure |

---

## Directory Structure

```
apps/
└── backend/
    └── agents/
        └── enterprise/
            ├── __init__.py                        # Enterprise agents exports
            ├── base_enterprise_agent.py           # LLM-agnostic base class
            ├── config.py                          # Agent LLM configuration
            ├── types.py                           # Enterprise agent types
            │
            ├── code_review/
            │   ├── __init__.py                    # Code review exports
            │   ├── code_review_agent.py           # PR/code review agent
            │   ├── review_result.py               # Structured review results
            │   ├── review_prompts.py              # Review prompt templates
            │   └── severity_classifier.py         # Finding severity classification
            │
            ├── security/
            │   ├── __init__.py                    # Security agents exports
            │   ├── security_agent.py              # Security vulnerability scanning
            │   ├── scan_result.py                 # Security scan results
            │   ├── vulnerability_db.py            # Known vulnerability patterns
            │   └── owasp_checker.py               # OWASP Top 10 compliance
            │
            ├── qa/
            │   ├── __init__.py                    # QA agents exports
            │   ├── qa_agent.py                    # Test generation agent
            │   ├── test_generator.py              # Test case generation
            │   ├── coverage_analyzer.py           # Coverage analysis
            │   └── test_templates.py              # Test templates by framework
            │
            ├── documentation/
            │   ├── __init__.py                    # Documentation agents exports
            │   ├── documentation_agent.py         # Doc generation agent
            │   ├── docstring_generator.py         # Auto-docstring generation
            │   ├── readme_generator.py            # README generation
            │   └── api_doc_generator.py           # API documentation
            │
            ├── project_analysis/
            │   ├── __init__.py                    # Project analysis exports
            │   ├── project_analyzer_agent.py      # Codebase analysis agent
            │   ├── dependency_mapper.py           # Dependency analysis
            │   ├── architecture_extractor.py      # Architecture inference
            │   └── tech_debt_analyzer.py          # Technical debt identification
            │
            ├── orchestration/
            │   ├── __init__.py                    # Orchestration exports
            │   ├── orchestrator_agent.py          # Multi-agent coordination
            │   ├── agent_coordinator.py           # Agent task distribution
            │   ├── result_aggregator.py           # Result aggregation
            │   └── pipeline_manager.py            # Pipeline execution
            │
            └── capabilities/
                ├── __init__.py                    # Capabilities exports
                ├── code_analysis.py               # Code analysis utilities
                ├── test_generation.py             # Test generation utilities
                ├── documentation.py               # Documentation utilities
                └── collaboration.py               # Inter-agent communication
```

---

## File Specifications

### 1. Core Enterprise Module (`enterprise/`)

#### `base_enterprise_agent.py`
**Purpose**: LLM-agnostic base class for all enterprise agents
**Key Components**:
```python
class BaseEnterpriseAgent:
    """
    Base class for enterprise agents with LLM-agnostic design.
    
    Each agent instance can use any of the 8 LLM providers.
    """
    
    def __init__(self, config: EnterpriseAgentConfig, llm_router: LLMRouter):
        """Initialize with LLM configuration."""
        self.config = config
        self.llm_router = llm_router
        
        # Validate LLM config - NO defaults allowed
        if not config.llm_config:
            raise ValueError(
                f"Agent {config.agent_id} has no LLM configured. "
                "Must assign provider from: copilot, openrouter, ollama, "
                "lmstudio, gemini, openai, anthropic, azure"
            )
        config.llm_config.validate()
    
    async def complete(self, prompt: str) -> str:
        """Complete using agent's configured LLM provider."""
        client = self.llm_router.get_client(
            provider=self.config.llm_config.provider,
            model=self.config.llm_config.model
        )
        return await client.complete(
            prompt=prompt,
            temperature=self.config.llm_config.temperature,
            max_tokens=self.config.llm_config.max_tokens,
        )
    
    async def complete_with_fallback(self, prompt: str) -> str:
        """Complete with automatic fallback on failure."""
        try:
            return await self.complete(prompt)
        except Exception:
            if self.config.llm_config.fallback_provider:
                fallback = self.llm_router.get_client(
                    provider=self.config.llm_config.fallback_provider,
                    model=self.config.llm_config.fallback_model
                )
                return await fallback.complete(prompt=prompt)
            raise
```

#### `config.py`
**Purpose**: Per-agent LLM configuration
**Key Components**:
```python
@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration."""
    provider: str  # One of 8: copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    
    SUPPORTED_PROVIDERS = [
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    ]
    
    def validate(self):
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Invalid provider: {self.provider}")


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
```

#### `types.py`
**Purpose**: Enterprise agent type definitions
**Key Components**:
```python
class EnterpriseAgentType(Enum):
    CODE_REVIEW = "code_review"
    SECURITY = "security"
    QA = "qa"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATOR = "orchestrator"


class AgentCapability(Enum):
    CODE_REVIEW = "code_review"
    SECURITY_SCAN = "security_scan"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATION = "orchestration"
```

---

### 2. Code Review Module (`enterprise/code_review/`)

#### `code_review_agent.py`
**Purpose**: Automated PR and code review
**Key Components**:
```python
class CodeReviewAgent(BaseEnterpriseAgent):
    """Agent for automated code review using configured LLM."""
    
    DEFAULT_SYSTEM_PROMPT = """You are an expert code reviewer..."""
    
    async def review_file(self, file_path: str, content: str, diff: Optional[str] = None) -> CodeReviewResult
    async def review_pr(self, pr_data: Dict) -> List[CodeReviewResult]
    async def suggest_improvements(self, code: str, language: str) -> List[Suggestion]
    async def check_best_practices(self, code: str, language: str) -> List[Finding]
```

#### `review_result.py`
**Purpose**: Structured code review results
**Key Components**:
```python
@dataclass
class CodeReviewResult:
    file_path: str
    findings: List[Finding]
    suggestions: List[Suggestion]
    severity_counts: Dict[str, int]
    overall_quality: float  # 0.0 - 1.0
    approved: bool


@dataclass
class Finding:
    id: str
    severity: Severity
    category: str
    message: str
    line_start: int
    line_end: Optional[int]
    suggestion: Optional[str]
```

#### `severity_classifier.py`
**Purpose**: Classify finding severity
**Key Components**:
- CRITICAL: Security vulnerabilities, data loss risks
- HIGH: Bugs, logic errors
- MEDIUM: Code quality issues
- LOW: Style, documentation
- INFO: Suggestions only

---

### 3. Security Module (`enterprise/security/`)

#### `security_agent.py`
**Purpose**: Security vulnerability scanning agent
**Key Components**:
```python
class SecurityAgent(BaseEnterpriseAgent):
    """Agent for security scanning using any of 8 LLM providers."""
    
    async def scan_code(self, code: str, language: str) -> SecurityScanResult
    async def check_owasp(self, code: str) -> List[OWASPFinding]
    async def scan_dependencies(self, lockfile: str) -> List[VulnerablePackage]
    async def generate_remediation(self, finding: SecurityFinding) -> str
```

#### `owasp_checker.py`
**Purpose**: OWASP Top 10 compliance checking
**Key Components**:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Authentication Failures
- A08: Data Integrity Failures
- A09: Logging Failures
- A10: SSRF

---

### 4. QA Module (`enterprise/qa/`)

#### `qa_agent.py`
**Purpose**: Test generation and quality assurance
**Key Components**:
```python
class QAAgent(BaseEnterpriseAgent):
    """Agent for test generation using configured LLM."""
    
    async def generate_tests(self, code: str, language: str, framework: str) -> str
    async def analyze_coverage(self, coverage_report: Dict) -> CoverageAnalysis
    async def suggest_test_cases(self, code: str) -> List[TestCase]
    async def generate_test_plan(self, feature_spec: str) -> TestPlan
```

#### `test_generator.py`
**Purpose**: Generate test cases
**Key Components**:
```python
class TestGenerator:
    def generate_unit_tests(self, code: str, language: str, framework: str) -> str
    def generate_integration_tests(self, api_spec: Dict) -> str
    def generate_edge_cases(self, function_code: str) -> List[str]
```

#### `test_templates.py`
**Purpose**: Framework-specific test templates
**Supported Frameworks**:
- Python: pytest, unittest
- JavaScript: Jest, Mocha, Vitest
- TypeScript: Jest, Vitest

---

### 5. Documentation Module (`enterprise/documentation/`)

#### `documentation_agent.py`
**Purpose**: Automated documentation generation
**Key Components**:
```python
class DocumentationAgent(BaseEnterpriseAgent):
    """Agent for documentation generation."""
    
    async def generate_docstrings(self, code: str, style: str = "google") -> str
    async def generate_readme(self, project_info: Dict) -> str
    async def generate_api_docs(self, api_spec: Dict) -> str
    async def update_changelog(self, changes: List[str]) -> str
```

---

### 6. Project Analysis Module (`enterprise/project_analysis/`)

#### `project_analyzer_agent.py`
**Purpose**: Codebase analysis and insights
**Key Components**:
```python
class ProjectAnalyzerAgent(BaseEnterpriseAgent):
    """Agent for codebase analysis."""
    
    async def analyze_project(self, project_path: str) -> ProjectAnalysis
    async def map_dependencies(self, project_path: str) -> DependencyGraph
    async def identify_tech_debt(self, project_path: str) -> List[TechDebtItem]
    async def infer_architecture(self, project_path: str) -> ArchitectureModel
```

---

### 7. Orchestration Module (`enterprise/orchestration/`)

#### `orchestrator_agent.py`
**Purpose**: Multi-agent coordination
**Key Components**:
```python
class OrchestratorAgent(BaseEnterpriseAgent):
    """Agent for coordinating multiple enterprise agents."""
    
    async def coordinate_review(self, pr_data: Dict) -> PipelineResult:
        """Coordinate code review + security + QA agents."""
        
    async def run_pipeline(self, pipeline: Pipeline) -> PipelineResult
    async def aggregate_results(self, results: List[AgentResult]) -> AggregatedResult
```

#### `pipeline_manager.py`
**Purpose**: Define and execute agent pipelines
**Key Components**:
```python
class Pipeline:
    stages: List[PipelineStage]
    parallel: bool = False
    fail_fast: bool = True


class PipelineManager:
    def define_pipeline(self, stages: List[PipelineStage]) -> Pipeline
    async def execute_pipeline(self, pipeline: Pipeline, context: Dict) -> PipelineResult
```

---

### 8. Capabilities Module (`enterprise/capabilities/`)

#### `code_analysis.py`
**Purpose**: Shared code analysis utilities
**Key Components**:
- AST parsing
- Language detection
- Complexity calculation
- Symbol extraction

#### `test_generation.py`
**Purpose**: Shared test generation utilities
**Key Components**:
- Test framework detection
- Mock generation
- Assertion generation

#### `documentation.py`
**Purpose**: Shared documentation utilities
**Key Components**:
- Docstring parsing
- Markdown generation
- Type inference for docs

#### `collaboration.py`
**Purpose**: Inter-agent communication
**Key Components**:
```python
class AgentMessage:
    sender_id: str
    receiver_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    correlation_id: str


class AgentCollaboration:
    async def send_message(self, message: AgentMessage) -> None
    async def receive_message(self, agent_id: str) -> AgentMessage
    async def broadcast(self, sender_id: str, payload: Dict) -> None
```

---

## Per-Agent LLM Configuration Examples

```python
# Different agents using different providers
AGENT_CONFIGURATIONS = {
    "code_review_agent": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
    },
    "security_agent": {
        "provider": "openai",
        "model": "gpt-4-turbo",
    },
    "qa_agent": {
        "provider": "gemini",
        "model": "gemini-1.5-pro",
    },
    "documentation_agent": {
        "provider": "openrouter",
        "model": "anthropic/claude-3-opus",
    },
    "project_analyzer": {
        "provider": "ollama",
        "model": "llama3:70b",
    },
}
```

---

## Integration Points

### With LLM Layer (Phase 2)
- All agents use LLMRouter for provider access
- Per-agent configuration stored in config

### With Security (Phase 6)
- SecurityAgent uses security module for pattern matching
- All agent outputs scanned for security

### With Orchestration (Phase 4)
- Agents receive tasks from TaskQueue
- OrchestratorAgent coordinates via AgentPool

### With Analytics (Phase 8)
- Agent performance tracked via metrics
- Cost tracking per agent/provider

---

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Agent initialization | <100ms | 500ms |
| Code review latency | <30s/file | 60s |
| Security scan latency | <10s/file | 30s |
| Test generation | <45s/function | 90s |
| LLM provider switch | <1s | 5s |
| Agent memory footprint | <256MB | 512MB |

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `enterprise/` (core) | 4 | Base configuration |
| `enterprise/code_review/` | 5 | Code review agent |
| `enterprise/security/` | 5 | Security agent |
| `enterprise/qa/` | 5 | QA/test agent |
| `enterprise/documentation/` | 5 | Documentation agent |
| `enterprise/project_analysis/` | 5 | Project analyzer |
| `enterprise/orchestration/` | 5 | Multi-agent coordination |
| `enterprise/capabilities/` | 5 | Shared capabilities |
| **Total** | **39** | Phase 7 files |

---

## Next Steps

→ Phase 8: Analytics & Tools Architecture

---

*Phase 7 Architecture complete. 39 files specified for enterprise agents.*
