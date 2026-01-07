"""Enterprise agent configuration with LLM-agnostic design.

World-Class Standards:
- Per-agent LLM assignment
- Fallback configuration
- Capability-based composition

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class AgentCapability(Enum):
    """Agent capability types for enterprise agents."""
    CODE_REVIEW = "code_review"
    SECURITY_SCAN = "security_scan"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    PROJECT_ANALYSIS = "project_analysis"
    ORCHESTRATION = "orchestration"
    CODE_ANALYSIS = "code_analysis"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"


@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration.
    
    Supports all 8 providers equally - NO defaults.
    Each agent can use any provider independently.
    
    Providers:
        - copilot: GitHub Copilot integration
        - openrouter: Multi-model access
        - ollama: Local/private deployment
        - lmstudio: Local development
        - gemini: Google ecosystem
        - openai: GPT models
        - anthropic: Claude models
        - azure: Enterprise Azure OpenAI
    """
    provider: str  # One of 8: copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str     # Provider-specific model ID
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout_seconds: int = 120
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    
    SUPPORTED_PROVIDERS: List[str] = field(
        default_factory=lambda: [
            "copilot", "openrouter", "ollama", "lmstudio",
            "gemini", "openai", "anthropic", "azure"
        ],
        repr=False,
    )
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Create default providers list if not set
        if not hasattr(self, '_providers'):
            self._providers = [
                "copilot", "openrouter", "ollama", "lmstudio",
                "gemini", "openai", "anthropic", "azure"
            ]
    
    def validate(self) -> None:
        """Validate provider is one of 8 supported.
        
        Raises:
            ValueError: If provider is not in the supported list.
        """
        supported = [
            "copilot", "openrouter", "ollama", "lmstudio",
            "gemini", "openai", "anthropic", "azure"
        ]
        if self.provider not in supported:
            raise ValueError(
                f"Invalid provider: {self.provider}. "
                f"Must be one of: {', '.join(supported)}"
            )
        if self.fallback_provider and self.fallback_provider not in supported:
            raise ValueError(
                f"Invalid fallback provider: {self.fallback_provider}. "
                f"Must be one of: {', '.join(supported)}"
            )
        if self.fallback_provider and not self.fallback_model:
            raise ValueError(
                "fallback_model is required when fallback_provider is set"
            )


@dataclass
class EnterpriseAgentConfig:
    """Complete enterprise agent configuration.
    
    World-Class Standards:
    - Explicit LLM configuration required (no defaults)
    - Capability-based agent composition
    - Memory and tool integration
    """
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
    
    def validate(self) -> None:
        """Validate the agent configuration.
        
        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not self.agent_id:
            raise ValueError("agent_id is required")
        if not self.agent_type:
            raise ValueError("agent_type is required")
        if not self.name:
            raise ValueError("name is required")
        if self.llm_config:
            self.llm_config.validate()


# Example configurations demonstrating LLM-agnostic design
AGENT_CONFIGURATION_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "code_review_agent": {
        "provider": "anthropic",      # Claude for nuanced review
        "model": "claude-sonnet-4-20250514",
    },
    "security_agent": {
        "provider": "openai",         # GPT for security analysis
        "model": "gpt-4-turbo",
    },
    "qa_agent": {
        "provider": "gemini",         # Gemini for test generation
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
    "orchestrator_agent": {
        "provider": "azure",          # Azure for enterprise
        "model": "gpt-4-turbo",
    },
}
