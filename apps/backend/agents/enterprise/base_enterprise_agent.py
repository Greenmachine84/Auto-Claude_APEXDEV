"""LLM-Agnostic Base Enterprise Agent.

World-Class Standards:
- Each agent instance can use any of the 8 LLM providers
- No default provider - must be explicitly configured
- Automatic fallback on failure
- Structured output validation

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md

Providers (Equal Support):
    - copilot: GitHub Copilot integration
    - openrouter: Multi-model access
    - ollama: Local/private deployment
    - lmstudio: Local development
    - gemini: Google ecosystem
    - openai: GPT models
    - anthropic: Claude models
    - azure: Enterprise Azure OpenAI
"""
from abc import abstractmethod
from typing import Any, ClassVar, Dict, List, Optional, Protocol
import logging
import time

from .config import AgentCapability, AgentLLMConfig, EnterpriseAgentConfig
from .types import EnterpriseAgentType


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Complete a prompt using the LLM."""
        ...


class LLMRouter(Protocol):
    """Protocol for LLM router implementations.
    
    Routes requests to any of the 8 supported providers.
    """
    
    def get_client(
        self,
        provider: str,
        model: str,
    ) -> LLMClient:
        """Get an LLM client for the specified provider and model."""
        ...


class BaseEnterpriseAgent:
    """Base class for enterprise agents with LLM-agnostic design.
    
    Each agent instance can use any of the 8 LLM providers.
    Different agents can use different providers simultaneously.
    NO default provider - all must be explicitly configured.
    
    Supported Providers:
        - copilot: GitHub Copilot integration
        - openrouter: Multi-model access  
        - ollama: Local/private deployment
        - lmstudio: Local development
        - gemini: Google ecosystem
        - openai: GPT models
        - anthropic: Claude models
        - azure: Enterprise Azure OpenAI
    
    Attributes:
        config: Agent configuration including LLM settings
        llm_router: Router to access any of 8 providers
        logger: Agent-specific logger
        capabilities: List of agent capabilities
    """
    
    # Subclasses should override
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.CODE_REVIEW
    AGENT_CATEGORY: ClassVar[str] = "enterprise"
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = "You are an expert enterprise agent."
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize agent with LLM configuration.
        
        Args:
            config: Agent configuration including LLM settings
            llm_router: Router to access any of 8 providers
            
        Raises:
            ValueError: If no LLM is configured (no defaults allowed)
        """
        self.config = config
        self.llm_router = llm_router
        self.logger = logging.getLogger(f"{__name__}.{config.agent_id}")
        self._metrics: Dict[str, Any] = {}
        self._call_count: int = 0
        self._total_latency: float = 0.0
        
        # Validate LLM config - NO defaults allowed
        if config.llm_config:
            config.llm_config.validate()
        else:
            self.logger.warning(
                f"Agent {config.agent_id} has no LLM configured. "
                "Must assign provider from: copilot, openrouter, ollama, "
                "lmstudio, gemini, openai, anthropic, azure"
            )
        
        # Validate full config
        config.validate()
    
    @property
    def id(self) -> str:
        """Get the agent ID."""
        return self.config.agent_id
    
    @property
    def name(self) -> str:
        """Get the agent name."""
        return self.config.name
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        """Get the agent's capabilities."""
        return self.config.capabilities
    
    @property
    def provider(self) -> Optional[str]:
        """Get the configured LLM provider."""
        if self.config.llm_config:
            return self.config.llm_config.provider
        return None
    
    @property
    def model(self) -> Optional[str]:
        """Get the configured model."""
        if self.config.llm_config:
            return self.config.llm_config.model
        return None
    
    @classmethod
    def get_description(cls) -> str:
        """Get a description of this agent type."""
        return f"{cls.AGENT_TYPE.value} enterprise agent"
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported LLM providers."""
        return [
            "copilot", "openrouter", "ollama", "lmstudio",
            "gemini", "openai", "anthropic", "azure"
        ]
    
    async def complete(self, prompt: str) -> str:
        """Complete prompt using agent's configured LLM provider.
        
        The LLM provider is determined by agent's llm_config.
        Automatically handles failover if configured.
        
        Args:
            prompt: The prompt to complete
            
        Returns:
            The LLM completion response
            
        Raises:
            ValueError: If no LLM is configured
            RuntimeError: If LLM router is not available
        """
        if not self.config.llm_config:
            raise ValueError(
                f"Agent {self.config.agent_id} has no LLM configured. "
                "Must assign provider from: copilot, openrouter, ollama, "
                "lmstudio, gemini, openai, anthropic, azure"
            )
        
        if not self.llm_router:
            raise RuntimeError(
                "LLM router not available. Cannot complete prompt."
            )
        
        start_time = time.time()
        self._call_count += 1
        
        try:
            client = self.llm_router.get_client(
                provider=self.config.llm_config.provider,
                model=self.config.llm_config.model,
            )
            
            result = await client.complete(
                prompt=prompt,
                temperature=self.config.llm_config.temperature,
                max_tokens=self.config.llm_config.max_tokens,
            )
            
            latency = time.time() - start_time
            self._total_latency += latency
            self._record_metric("last_latency", latency)
            self._record_metric("provider_used", self.config.llm_config.provider)
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"LLM completion failed with {self.config.llm_config.provider}: {e}"
            )
            return await self._handle_fallback(prompt, e)
    
    async def complete_with_fallback(self, prompt: str) -> str:
        """Complete with explicit fallback handling.
        
        Same as complete() but makes fallback behavior explicit.
        
        Args:
            prompt: The prompt to complete
            
        Returns:
            The LLM completion response
        """
        return await self.complete(prompt)
    
    async def _handle_fallback(
        self,
        prompt: str,
        original_error: Exception,
    ) -> str:
        """Handle fallback to secondary provider.
        
        Args:
            prompt: The original prompt
            original_error: The error from the primary provider
            
        Returns:
            The fallback LLM completion response
            
        Raises:
            RuntimeError: If fallback also fails or is not configured
        """
        if not self.config.llm_config:
            raise RuntimeError("No LLM configured") from original_error
        
        if not self.config.llm_config.fallback_provider:
            self.logger.error("No fallback provider configured")
            raise RuntimeError(
                f"Primary provider {self.config.llm_config.provider} failed "
                "and no fallback configured"
            ) from original_error
        
        if not self.llm_router:
            raise RuntimeError("LLM router not available") from original_error
        
        self.logger.warning(
            f"Falling back from {self.config.llm_config.provider} to "
            f"{self.config.llm_config.fallback_provider}"
        )
        
        try:
            fallback_client = self.llm_router.get_client(
                provider=self.config.llm_config.fallback_provider,
                model=self.config.llm_config.fallback_model or "",
            )
            
            result = await fallback_client.complete(
                prompt=prompt,
                temperature=self.config.llm_config.temperature,
                max_tokens=self.config.llm_config.max_tokens,
            )
            
            self._record_metric(
                "fallback_used",
                self.config.llm_config.fallback_provider,
            )
            
            return result
            
        except Exception as fallback_error:
            self.logger.error(
                f"Fallback provider {self.config.llm_config.fallback_provider} "
                f"also failed: {fallback_error}"
            )
            raise RuntimeError(
                f"Both primary ({self.config.llm_config.provider}) and "
                f"fallback ({self.config.llm_config.fallback_provider}) failed"
            ) from fallback_error
    
    def _record_metric(self, name: str, value: Any) -> None:
        """Record a metric."""
        self._metrics[name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get recorded metrics.
        
        Returns:
            Dictionary of metric name to value
        """
        return {
            **self._metrics,
            "call_count": self._call_count,
            "total_latency": self._total_latency,
            "avg_latency": (
                self._total_latency / self._call_count
                if self._call_count > 0
                else 0.0
            ),
        }
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to this agent."""
        if capability not in self.config.capabilities:
            self.config.capabilities.append(capability)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.config.capabilities
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function.
        
        Args:
            context: Execution context with task details
            
        Returns:
            Execution result
        """
        pass
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.config.agent_id!r}, "
            f"type={self.AGENT_TYPE.value!r}, "
            f"provider={self.provider!r}"
            f")"
        )
