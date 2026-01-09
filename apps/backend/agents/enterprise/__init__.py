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
# API Agents
from .api_designer_agent import APIDesignerAgent
from .api_documenter_agent import APIDocumenterAgent
from .architect_agent import ArchitectAgent
from .base_enterprise_agent import BaseEnterpriseAgent
from .capabilities import (
    AnalysisResult as CapabilityAnalysisResult,
)

# Phase 7: Capabilities Module
from .capabilities import (
    CodeAnalysisCapability,
    CollaborationCapability,
    DocOutput,
    DocumentationCapability,
    Message,
    TestGenerationCapability,
    TestSuite,
)
from .changelog_generator_agent import ChangelogGeneratorAgent

# Phase 7: Code Review Module
from .code_review import (
    CodeReviewAgent,
    ReviewFinding,
    ReviewPrompts,
    ReviewResult,
    SeverityClassifier,
)
from .compliance_checker_agent import ComplianceCheckerAgent

# Phase 7: Core LLM-Agnostic Infrastructure
from .config import AgentCapability, AgentLLMConfig, EnterpriseAgentConfig, LLMProvider
from .coverage_agent import CoverageAgent
from .documentation import (
    APIDocGenerator,
    APIEndpoint,
    DocstringGenerator,
    GeneratedDocstring,
    ReadmeGenerator,
    ReadmeSection,
)

# Phase 7: Documentation Module
from .documentation import (
    DocumentationAgent as DocumentationAgentV2,
)

# Documentation Agents
from .documentation_agent import DocumentationAgent
from .migration_agent import MigrationAgent

# Phase 7: Orchestration Module
from .orchestration import (
    AgentCoordinator,
    AggregatedResult,
    CoordinationResult,
    OrchestratorAgent,
    Pipeline,
    PipelineManager,
    PipelineStage,
    ResultAggregator,
)
from .performance_analyzer_agent import PerformanceAnalyzerAgent

# Phase 7: Project Analysis Module
from .project_analysis import (
    ArchitectureExtractor,
    ArchitectureMap,
    DependencyGraph,
    DependencyMapper,
    ProjectAnalyzerAgent,
    TechDebtAnalyzer,
    TechDebtReport,
)

# Phase 7: QA Module
from .qa import (
    CoverageAnalyzer,
    CoverageReport,
    GeneratedTest,
    QAAgent,
    TestGenerator,
    TestTemplate,
    TestTemplates,
)
from .schema_validator_agent import SchemaValidatorAgent

# Phase 7: Security Module
from .security import (
    OWASPChecker,
    ScanResult,
    SecretFinding,
    SecurityAgent,
    VulnerabilityDB,
    VulnerabilityFinding,
)

# Security Agents
from .security_scanner_agent import SecurityScannerAgent
from .system_designer_agent import SystemDesignerAgent

# Orchestration Agents
from .task_coordinator_agent import TaskCoordinatorAgent

# Quality Agents
from .test_generator_agent import TestGeneratorAgent
from .types import EnterpriseAgentType, Severity
from .vulnerability_analyzer_agent import VulnerabilityAnalyzerAgent
from .workflow_manager_agent import WorkflowManagerAgent

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
    "VulnerabilityFinding",
    "SecretFinding",
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

# Enterprise Agent Registry
# Maps EnterpriseAgentType categories to their implementing agents
# Note: These use EnterpriseAgentType (simplified 6-category system)
# while the core registry uses AgentType (full 20-type system)

ENTERPRISE_AGENT_REGISTRY: dict[EnterpriseAgentType, list[type]] = {
    EnterpriseAgentType.PROJECT_ANALYSIS: [
        ArchitectAgent,
        SystemDesignerAgent,
        MigrationAgent,
    ],
    EnterpriseAgentType.SECURITY: [
        SecurityScannerAgent,
        VulnerabilityAnalyzerAgent,
        ComplianceCheckerAgent,
    ],
    EnterpriseAgentType.QA: [
        TestGeneratorAgent,
        PerformanceAnalyzerAgent,
        CoverageAgent,
    ],
    EnterpriseAgentType.DOCUMENTATION: [
        DocumentationAgent,
        APIDocumenterAgent,
        ChangelogGeneratorAgent,
    ],
    EnterpriseAgentType.CODE_REVIEW: [
        APIDesignerAgent,
        SchemaValidatorAgent,
    ],
    EnterpriseAgentType.ORCHESTRATOR: [
        TaskCoordinatorAgent,
        WorkflowManagerAgent,
    ],
}


def get_enterprise_agents_by_type(agent_type: EnterpriseAgentType) -> list[type]:
    """Get all enterprise agent classes for a given type.

    Args:
        agent_type: The enterprise agent type category

    Returns:
        List of agent classes in that category
    """
    return ENTERPRISE_AGENT_REGISTRY.get(agent_type, [])


def get_all_enterprise_agents() -> list[type]:
    """Get all enterprise agent classes.

    Returns:
        List of all enterprise agent classes
    """
    return [agent for agents in ENTERPRISE_AGENT_REGISTRY.values() for agent in agents]
