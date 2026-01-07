"""Enterprise Agents Module.

Implements the 16 enterprise agents defined in PHASE1_AGENT_SYSTEM_ARCHITECTURE.md.
Organized by category for maintainability.

Categories:
- Architecture: Architect, SystemDesigner, MigrationAgent
- Security: SecurityScanner, VulnerabilityAnalyzer, ComplianceChecker
- Quality: TestGenerator, PerformanceAnalyzer, CoverageAgent
- Documentation: DocumentationAgent, APIDocumenter, ChangelogGenerator
- API: APIDesigner, SchemaValidator
- Orchestration: TaskCoordinator, WorkflowManager

Phase 7 Additions:
- Core: AgentLLMConfig, EnterpriseAgentConfig, LLM-agnostic base class
- Subdirectories: code_review, security, qa, documentation, project_analysis, 
                  orchestration, capabilities
"""

# Architecture Agents
from .architect_agent import ArchitectAgent
from .system_designer_agent import SystemDesignerAgent
from .migration_agent import MigrationAgent

# Security Agents
from .security_scanner_agent import SecurityScannerAgent
from .vulnerability_analyzer_agent import VulnerabilityAnalyzerAgent
from .compliance_checker_agent import ComplianceCheckerAgent

# Quality Agents
from .test_generator_agent import TestGeneratorAgent
from .performance_analyzer_agent import PerformanceAnalyzerAgent
from .coverage_agent import CoverageAgent

# Documentation Agents
from .documentation_agent import DocumentationAgent
from .api_documenter_agent import APIDocumenterAgent
from .changelog_generator_agent import ChangelogGeneratorAgent

# API Agents
from .api_designer_agent import APIDesignerAgent
from .schema_validator_agent import SchemaValidatorAgent

# Orchestration Agents
from .task_coordinator_agent import TaskCoordinatorAgent
from .workflow_manager_agent import WorkflowManagerAgent

# Phase 7: Core LLM-Agnostic Infrastructure
from .config import AgentLLMConfig, EnterpriseAgentConfig, LLMProvider
from .types import EnterpriseAgentType, Severity, AgentCapability
from .base_enterprise_agent import BaseEnterpriseAgent

# Phase 7: Code Review Module
from .code_review import (
    CodeReviewAgent,
    ReviewResult,
    ReviewFinding,
    ReviewPrompts,
    SeverityClassifier,
)

# Phase 7: Security Module
from .security import (
    SecurityAgent,
    ScanResult,
    SecurityFinding,
    VulnerabilityDB,
    OWASPChecker,
)

# Phase 7: QA Module
from .qa import (
    QAAgent,
    TestResult,
    TestGenerator,
    CoverageAnalyzer,
    TestTemplates,
)

# Phase 7: Documentation Module
from .documentation import (
    DocumentationAgentV2,
    DocResult,
    DocstringGenerator,
    ReadmeGenerator,
    APIDocGenerator,
)

# Phase 7: Project Analysis Module
from .project_analysis import (
    ProjectAnalyzerAgent,
    AnalysisResult,
    DependencyMapper,
    ArchitectureExtractor,
    TechDebtAnalyzer,
)

# Phase 7: Orchestration Module
from .orchestration import (
    OrchestratorAgent,
    OrchestrationResult,
    AgentCoordinator,
    ResultAggregator,
    PipelineManager,
)

# Phase 7: Capabilities Module
from .capabilities import (
    CodeAnalysisCapability,
    AnalysisResult as CapabilityAnalysisResult,
    TestGenerationCapability,
    TestSuite,
    DocumentationCapability,
    DocOutput,
    CollaborationCapability,
    Message,
)

__all__ = [
    # Architecture (Legacy)
    "ArchitectAgent",
    "SystemDesignerAgent",
    "MigrationAgent",
    # Security (Legacy)
    "SecurityScannerAgent",
    "VulnerabilityAnalyzerAgent",
    "ComplianceCheckerAgent",
    # Quality (Legacy)
    "TestGeneratorAgent",
    "PerformanceAnalyzerAgent",
    "CoverageAgent",
    # Documentation (Legacy)
    "DocumentationAgent",
    "APIDocumenterAgent",
    "ChangelogGeneratorAgent",
    # API (Legacy)
    "APIDesignerAgent",
    "SchemaValidatorAgent",
    # Orchestration (Legacy)
    "TaskCoordinatorAgent",
    "WorkflowManagerAgent",
    # Phase 7: Core
    "AgentLLMConfig",
    "EnterpriseAgentConfig",
    "LLMProvider",
    "EnterpriseAgentType",
    "Severity",
    "AgentCapability",
    "BaseEnterpriseAgent",
    # Phase 7: Code Review
    "CodeReviewAgent",
    "ReviewResult",
    "ReviewFinding",
    "ReviewPrompts",
    "SeverityClassifier",
    # Phase 7: Security
    "SecurityAgent",
    "ScanResult",
    "SecurityFinding",
    "VulnerabilityDB",
    "OWASPChecker",
    # Phase 7: QA
    "QAAgent",
    "TestResult",
    "TestGenerator",
    "CoverageAnalyzer",
    "TestTemplates",
    # Phase 7: Documentation
    "DocumentationAgentV2",
    "DocResult",
    "DocstringGenerator",
    "ReadmeGenerator",
    "APIDocGenerator",
    # Phase 7: Project Analysis
    "ProjectAnalyzerAgent",
    "AnalysisResult",
    "DependencyMapper",
    "ArchitectureExtractor",
    "TechDebtAnalyzer",
    # Phase 7: Orchestration
    "OrchestratorAgent",
    "OrchestrationResult",
    "AgentCoordinator",
    "ResultAggregator",
    "PipelineManager",
    # Phase 7: Capabilities
    "CodeAnalysisCapability",
    "CapabilityAnalysisResult",
    "TestGenerationCapability",
    "TestSuite",
    "DocumentationCapability",
    "DocOutput",
    "CollaborationCapability",
    "Message",
]

# Register all enterprise agents on import
from ..registry import get_registry
from ..types import AgentType

_registry = get_registry()

# Architecture
_registry.register_class(AgentType.ARCHITECT, ArchitectAgent, override=True)
_registry.register_class(AgentType.SYSTEM_DESIGNER, SystemDesignerAgent, override=True)
_registry.register_class(AgentType.MIGRATION, MigrationAgent, override=True)

# Security
_registry.register_class(AgentType.SECURITY_SCANNER, SecurityScannerAgent, override=True)
_registry.register_class(AgentType.VULNERABILITY_ANALYZER, VulnerabilityAnalyzerAgent, override=True)
_registry.register_class(AgentType.COMPLIANCE_CHECKER, ComplianceCheckerAgent, override=True)

# Quality
_registry.register_class(AgentType.TEST_GENERATOR, TestGeneratorAgent, override=True)
_registry.register_class(AgentType.PERFORMANCE_ANALYZER, PerformanceAnalyzerAgent, override=True)
_registry.register_class(AgentType.COVERAGE, CoverageAgent, override=True)

# Documentation
_registry.register_class(AgentType.DOCUMENTATION, DocumentationAgent, override=True)
_registry.register_class(AgentType.API_DOCUMENTER, APIDocumenterAgent, override=True)
_registry.register_class(AgentType.CHANGELOG_GENERATOR, ChangelogGeneratorAgent, override=True)

# API
_registry.register_class(AgentType.API_DESIGNER, APIDesignerAgent, override=True)
_registry.register_class(AgentType.SCHEMA_VALIDATOR, SchemaValidatorAgent, override=True)

# Orchestration
_registry.register_class(AgentType.TASK_COORDINATOR, TaskCoordinatorAgent, override=True)
_registry.register_class(AgentType.WORKFLOW_MANAGER, WorkflowManagerAgent, override=True)
