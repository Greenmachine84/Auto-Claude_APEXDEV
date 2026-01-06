# Phase 7: Enterprise Agents

> **Duration**: Week 13-14 | **Priority**: 🟡 MEDIUM
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| CodeReviewAgent functional | PR analysis works | ✅ |
| SecurityAgent functional | Vulnerability scanning | ✅ |
| QAAgent functional | Test generation | ✅ |
| ProjectAnalyzerAgent functional | Codebase analysis | ✅ |
| Agent LLM assignment | Per-agent provider/model | ✅ |
| Agent collaboration | Inter-agent communication | ✅ |

### Deliverables

1. `apps/backend/agents/enterprise/code_review_agent.py`
2. `apps/backend/agents/enterprise/security_agent.py`
3. `apps/backend/agents/enterprise/qa_agent.py`
4. `apps/backend/agents/enterprise/project_analyzer_agent.py`
5. `apps/backend/agents/enterprise/documentation_agent.py`
6. `apps/backend/agents/enterprise/orchestrator_agent.py`
7. Unit tests for all agents

---

## Section 1: Enterprise Agent Architecture

### Task 1.1: Directory Structure

```
apps/backend/agents/enterprise/
├── __init__.py
├── base_enterprise_agent.py    # From Phase 1
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

---

### Task 1.2: Agent Configuration Model

**File**: `apps/backend/agents/enterprise/config.py`

```python
"""Enterprise agent configuration."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class AgentCapability(Enum):
    CODE_REVIEW = "code_review"
    SECURITY_SCAN = "security_scan"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATION = "orchestration"

@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration (LLM-agnostic)."""
    provider: str           # copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str             # Provider-specific model ID
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None

@dataclass
class EnterpriseAgentConfig:
    """Configuration for enterprise agent."""
    agent_id: str
    agent_type: str
    name: str
    description: str = ""
    llm_config: Optional[AgentLLMConfig] = None  # Uses user default if None
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
"""Code review agent for PR analysis."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability

@dataclass
class CodeReviewResult:
    """Result of code review."""
    file_path: str
    findings: List[Dict[str, Any]]
    suggestions: List[str]
    severity_counts: Dict[str, int]
    overall_quality: float  # 0-100
    approved: bool

@dataclass
class PRReviewResult:
    """Result of full PR review."""
    pr_id: str
    file_reviews: List[CodeReviewResult]
    summary: str
    overall_approved: bool
    blocking_issues: List[str]
    suggestions: List[str]

class CodeReviewAgent(BaseEnterpriseAgent):
    """Agent for automated code review."""
    
    DEFAULT_SYSTEM_PROMPT = """You are an expert code reviewer. 
Analyze code changes for:
1. Code quality and best practices
2. Potential bugs and edge cases
3. Performance issues
4. Security vulnerabilities
5. Documentation and readability

Provide constructive, actionable feedback."""
    
    def __init__(self, config: EnterpriseAgentConfig):
        super().__init__(config)
        self.config.capabilities.append(AgentCapability.CODE_REVIEW)
    
    async def review_file(
        self, 
        file_path: str,
        content: str,
        diff: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CodeReviewResult:
        """Review a single file."""
        prompt = self._build_review_prompt(file_path, content, diff, context)
        
        # Use agent's configured LLM
        response = await self.complete(prompt)
        
        # Parse structured response
        return self._parse_review_response(file_path, response)
    
    async def review_pr(
        self,
        pr_id: str,
        files: List[Dict[str, Any]],  # {path, content, diff}
        pr_description: Optional[str] = None
    ) -> PRReviewResult:
        """Review entire pull request."""
        file_reviews = []
        
        for file in files:
            review = await self.review_file(
                file_path=file["path"],
                content=file["content"],
                diff=file.get("diff"),
                context={"pr_description": pr_description}
            )
            file_reviews.append(review)
        
        # Generate summary
        summary = await self._generate_pr_summary(file_reviews, pr_description)
        
        blocking = [
            f"{r.file_path}: {issue}" 
            for r in file_reviews 
            for issue in r.findings 
            if issue.get("severity") == "blocking"
        ]
        
        return PRReviewResult(
            pr_id=pr_id,
            file_reviews=file_reviews,
            summary=summary,
            overall_approved=len(blocking) == 0,
            blocking_issues=blocking,
            suggestions=[s for r in file_reviews for s in r.suggestions],
        )
    
    def _build_review_prompt(
        self,
        file_path: str,
        content: str,
        diff: Optional[str],
        context: Optional[Dict]
    ) -> str:
        prompt = f"""Review the following code:

File: {file_path}

```
{content}
```
"""
        if diff:
            prompt += f"\nChanges (diff):\n```diff\n{diff}\n```\n"
        
        if context and context.get("pr_description"):
            prompt += f"\nPR Description: {context['pr_description']}\n"
        
        prompt += """
Provide review in JSON format:
{
    "findings": [{"type": "...", "severity": "...", "line": N, "message": "..."}],
    "suggestions": ["..."],
    "quality_score": 0-100,
    "approved": true/false
}"""
        return prompt
    
    def _parse_review_response(self, file_path: str, response: str) -> CodeReviewResult:
        # Parse JSON response
        import json
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = {"findings": [], "suggestions": [], "quality_score": 50, "approved": True}
        
        severity_counts = {}
        for finding in data.get("findings", []):
            sev = finding.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return CodeReviewResult(
            file_path=file_path,
            findings=data.get("findings", []),
            suggestions=data.get("suggestions", []),
            severity_counts=severity_counts,
            overall_quality=data.get("quality_score", 50),
            approved=data.get("approved", True),
        )
    
    async def _generate_pr_summary(
        self, 
        reviews: List[CodeReviewResult],
        pr_description: Optional[str]
    ) -> str:
        """Generate overall PR summary."""
        total_findings = sum(len(r.findings) for r in reviews)
        avg_quality = sum(r.overall_quality for r in reviews) / len(reviews) if reviews else 0
        
        prompt = f"""Summarize this code review:
- Files reviewed: {len(reviews)}
- Total findings: {total_findings}
- Average quality: {avg_quality:.1f}/100

Provide a concise summary paragraph."""
        
        return await self.complete(prompt)
```

---

## Section 3: Security Agent

### Task 3.1: Security Agent

**File**: `apps/backend/agents/enterprise/security_agent.py`

```python
"""Security scanning agent."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability
from ..security.scanner.secrets_scanner import SecretsScanner
from ..security.scanner.prompt_injection import PromptInjectionDefense

@dataclass
class SecurityScanResult:
    """Security scan results."""
    scan_id: str
    target: str  # file, directory, or input
    vulnerabilities: List[Dict[str, Any]]
    secrets_found: List[Dict[str, Any]]
    risk_score: float  # 0-100 (higher = more risk)
    recommendations: List[str]
    passed: bool

class SecurityAgent(BaseEnterpriseAgent):
    """Agent for security vulnerability scanning."""
    
    DEFAULT_SYSTEM_PROMPT = """You are a security expert.
Analyze code for:
1. Security vulnerabilities (OWASP Top 10)
2. Exposed secrets and credentials
3. Injection vulnerabilities
4. Authentication/authorization issues
5. Data exposure risks

Provide severity ratings and remediation steps."""
    
    def __init__(self, config: EnterpriseAgentConfig):
        super().__init__(config)
        self.config.capabilities.append(AgentCapability.SECURITY_SCAN)
        self.secrets_scanner = SecretsScanner()
        self.injection_defense = PromptInjectionDefense()
    
    async def scan_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> SecurityScanResult:
        """Scan code for security issues."""
        import uuid
        
        # Static analysis for secrets
        secrets = self.secrets_scanner.scan_text(code, file_path or "input")
        
        # LLM-based vulnerability analysis
        prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

Provide findings in JSON:
{{
    "vulnerabilities": [
        {{"type": "...", "severity": "critical|high|medium|low", "line": N, "description": "...", "remediation": "..."}}
    ],
    "risk_score": 0-100,
    "recommendations": ["..."]
}}"""
        
        response = await self.complete(prompt)
        
        import json
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = {"vulnerabilities": [], "risk_score": 0, "recommendations": []}
        
        # Combine findings
        all_vulns = data.get("vulnerabilities", [])
        secrets_as_vulns = [
            {
                "type": "exposed_secret",
                "severity": s.severity.value,
                "line": s.line_number,
                "description": s.message,
                "remediation": s.remediation,
            }
            for s in secrets
        ]
        
        risk_score = data.get("risk_score", 0)
        if secrets:
            risk_score = max(risk_score, 80)  # Secrets always high risk
        
        return SecurityScanResult(
            scan_id=str(uuid.uuid4()),
            target=file_path or "code_input",
            vulnerabilities=all_vulns,
            secrets_found=secrets_as_vulns,
            risk_score=risk_score,
            recommendations=data.get("recommendations", []),
            passed=risk_score < 50 and len(secrets) == 0,
        )
    
    async def validate_input(
        self,
        user_input: str
    ) -> Dict[str, Any]:
        """Validate user input for injection attempts."""
        is_suspicious, findings = self.injection_defense.analyze(user_input)
        
        return {
            "safe": not is_suspicious,
            "findings": [f.__dict__ for f in findings],
            "sanitized_input": self.injection_defense.sanitize(user_input),
        }
```

---

## Section 4: QA Agent

### Task 4.1: QA Agent

**File**: `apps/backend/agents/enterprise/qa_agent.py`

```python
"""QA and test generation agent."""
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
    test_type: str  # unit, integration, e2e
    target_function: Optional[str] = None
    target_file: Optional[str] = None

@dataclass
class TestGenerationResult:
    """Test generation results."""
    target: str
    test_cases: List[TestCase]
    framework: str  # pytest, jest, etc.
    coverage_estimate: float

class QAAgent(BaseEnterpriseAgent):
    """Agent for test generation and QA."""
    
    DEFAULT_SYSTEM_PROMPT = """You are a QA engineer expert.
Generate comprehensive tests including:
1. Unit tests for individual functions
2. Edge case tests
3. Error handling tests
4. Integration tests where appropriate

Follow testing best practices and use appropriate assertions."""
    
    def __init__(self, config: EnterpriseAgentConfig):
        super().__init__(config)
        self.config.capabilities.append(AgentCapability.TEST_GENERATION)
    
    async def generate_tests(
        self,
        code: str,
        language: str,
        framework: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> TestGenerationResult:
        """Generate tests for code."""
        # Detect framework
        if not framework:
            framework = self._detect_framework(language)
        
        prompt = f"""Generate {framework} tests for this {language} code:

```{language}
{code}
```

Generate comprehensive test cases. Return JSON:
{{
    "test_cases": [
        {{
            "name": "test_function_name",
            "description": "What it tests",
            "test_code": "full test code",
            "test_type": "unit|integration",
            "target_function": "function being tested"
        }}
    ],
    "coverage_estimate": 0-100
}}"""
        
        response = await self.complete(prompt)
        
        import json
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = {"test_cases": [], "coverage_estimate": 0}
        
        test_cases = [
            TestCase(
                name=tc.get("name", "test_unknown"),
                description=tc.get("description", ""),
                test_code=tc.get("test_code", ""),
                test_type=tc.get("test_type", "unit"),
                target_function=tc.get("target_function"),
                target_file=file_path,
            )
            for tc in data.get("test_cases", [])
        ]
        
        return TestGenerationResult(
            target=file_path or "code_input",
            test_cases=test_cases,
            framework=framework,
            coverage_estimate=data.get("coverage_estimate", 0),
        )
    
    def _detect_framework(self, language: str) -> str:
        """Detect appropriate test framework."""
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "go": "testing",
            "rust": "cargo test",
        }
        return frameworks.get(language.lower(), "pytest")
```

---

## Section 5: Project Analyzer Agent

### Task 5.1: Project Analyzer

**File**: `apps/backend/agents/enterprise/project_analyzer_agent.py`

```python
"""Project analysis agent."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from .base_enterprise_agent import BaseEnterpriseAgent
from .config import EnterpriseAgentConfig, AgentCapability

@dataclass
class ProjectAnalysis:
    """Project analysis result."""
    project_type: str  # python, nodejs, java, etc.
    frameworks: List[str]
    dependencies: Dict[str, str]
    structure: Dict[str, Any]
    entry_points: List[str]
    configuration_files: List[str]
    test_coverage: Optional[float] = None
    documentation_coverage: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)

class ProjectAnalyzerAgent(BaseEnterpriseAgent):
    """Agent for codebase analysis."""
    
    DEFAULT_SYSTEM_PROMPT = """You are a software architect.
Analyze codebases for:
1. Project structure and organization
2. Technologies and frameworks used
3. Architecture patterns
4. Potential improvements
5. Technical debt

Provide actionable insights."""
    
    def __init__(self, config: EnterpriseAgentConfig):
        super().__init__(config)
        self.config.capabilities.append(AgentCapability.PROJECT_ANALYSIS)
    
    async def analyze_project(
        self,
        project_path: str,
        include_patterns: Optional[List[str]] = None
    ) -> ProjectAnalysis:
        """Analyze project structure."""
        path = Path(project_path)
        
        # Detect project type
        project_type = await self._detect_project_type(path)
        
        # Find configuration files
        config_files = self._find_config_files(path)
        
        # Parse dependencies
        deps = await self._parse_dependencies(path, project_type)
        
        # Build structure map
        structure = self._build_structure(path, include_patterns)
        
        # Find entry points
        entry_points = await self._find_entry_points(path, project_type)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            project_type, structure, deps
        )
        
        return ProjectAnalysis(
            project_type=project_type,
            frameworks=list(deps.keys())[:10],
            dependencies=deps,
            structure=structure,
            entry_points=entry_points,
            configuration_files=config_files,
            recommendations=recommendations,
        )
    
    async def _detect_project_type(self, path: Path) -> str:
        """Detect project type from markers."""
        markers = {
            "package.json": "nodejs",
            "requirements.txt": "python",
            "pyproject.toml": "python",
            "Cargo.toml": "rust",
            "go.mod": "go",
            "pom.xml": "java",
            "build.gradle": "java",
        }
        for marker, ptype in markers.items():
            if (path / marker).exists():
                return ptype
        return "unknown"
    
    def _find_config_files(self, path: Path) -> List[str]:
        """Find configuration files."""
        config_patterns = [
            "*.json", "*.yaml", "*.yml", "*.toml", 
            ".env*", "*.config.js", "*.config.ts"
        ]
        configs = []
        for pattern in config_patterns:
            for f in path.glob(pattern):
                if f.is_file():
                    configs.append(str(f.relative_to(path)))
        return configs[:20]
    
    async def _parse_dependencies(self, path: Path, project_type: str) -> Dict[str, str]:
        """Parse dependencies from manifest."""
        import json
        deps = {}
        
        if project_type == "nodejs":
            pkg_json = path / "package.json"
            if pkg_json.exists():
                data = json.loads(pkg_json.read_text())
                deps.update(data.get("dependencies", {}))
                deps.update(data.get("devDependencies", {}))
        
        elif project_type == "python":
            req_txt = path / "requirements.txt"
            if req_txt.exists():
                for line in req_txt.read_text().splitlines():
                    if "==" in line:
                        name, ver = line.split("==", 1)
                        deps[name.strip()] = ver.strip()
        
        return deps
    
    def _build_structure(self, path: Path, include: Optional[List[str]]) -> Dict:
        """Build directory structure."""
        structure = {"dirs": [], "files": []}
        for item in path.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_dir():
                structure["dirs"].append(item.name)
            else:
                structure["files"].append(item.name)
        return structure
    
    async def _find_entry_points(self, path: Path, project_type: str) -> List[str]:
        """Find main entry points."""
        entries = []
        patterns = {
            "python": ["main.py", "app.py", "__main__.py"],
            "nodejs": ["index.js", "app.js", "server.js", "index.ts"],
        }
        for pattern in patterns.get(project_type, []):
            if (path / pattern).exists():
                entries.append(pattern)
        return entries
    
    async def _generate_recommendations(
        self, 
        project_type: str,
        structure: Dict,
        deps: Dict
    ) -> List[str]:
        """Generate improvement recommendations."""
        prompt = f"""Analyze this {project_type} project and suggest improvements:

Structure: {structure}
Dependencies: {list(deps.keys())[:20]}

Provide 3-5 actionable recommendations."""
        
        response = await self.complete(prompt)
        return [r.strip() for r in response.split("\n") if r.strip()]
```

---

## Section 6: Orchestrator Agent

### Task 6.1: Meta-Orchestrator Agent

**File**: `apps/backend/agents/enterprise/orchestrator_agent.py`

**Purpose**: Coordinates other agents, decides which agents to invoke.

---

## Validation Checklist

- [ ] CodeReviewAgent reviews files correctly
- [ ] SecurityAgent detects vulnerabilities
- [ ] QAAgent generates valid tests
- [ ] ProjectAnalyzerAgent analyzes projects
- [ ] Each agent uses its configured LLM
- [ ] Agents can collaborate via message bus
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1, 2, 4, 5, 6

**Enables**: Phase 8 (Analytics/Tools)

---

## ADR References

- ADR-001: Agent Architecture Unification
- ADR-005: LLM Agnostic Architecture
- ADR-013: Per-Agent LLM Configuration

---

*Phase 7 Specification v1.0.0*
