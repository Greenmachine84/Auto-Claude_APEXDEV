"""Fallback handler for LLM failures.

Part of Phase 2: LLM Architecture
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from ..types import FallbackConfig, FallbackTrigger, ProviderType, LLMResponse

if TYPE_CHECKING:
    from .provider_registry import ProviderRegistry
    from .llm_manager import ChatRequest

logger = logging.getLogger(__name__)


@dataclass
class FallbackResult:
    """Result of fallback execution."""
    success: bool
    provider_used: Optional[ProviderType] = None
    attempts: int = 0
    errors: List[str] = field(default_factory=list)
    response: Optional[LLMResponse] = None


class FallbackHandler:
    """Handles fallback when primary providers fail."""
    
    def __init__(self, config: FallbackConfig, registry: "ProviderRegistry"):
        self._config = config
        self._registry = registry
        self._failure_counts: Dict[ProviderType, int] = {}
    
    async def execute(self, request: "ChatRequest") -> LLMResponse:
        result = FallbackResult(success=False)
        
        chain = self._get_fallback_chain(request.provider)
        
        for provider_type in chain:
            result.attempts += 1
            
            provider = self._registry.get(provider_type)
            if not provider or not self._registry.is_available(provider_type):
                continue
            
            try:
                response = await provider.chat(
                    messages=request.messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    tools=request.tools
                )
                
                result.success = True
                result.provider_used = provider_type
                result.response = response
                
                self._failure_counts[provider_type] = 0
                logger.info("Fallback succeeded with %s after %d attempts", 
                           provider_type.value, result.attempts)
                return response
                
            except Exception as e:
                result.errors.append(f"{provider_type.value}: {e}")
                self._failure_counts[provider_type] = self._failure_counts.get(provider_type, 0) + 1
                logger.warning("Fallback attempt %d failed: %s", result.attempts, e)
        
        raise RuntimeError(f"All fallback attempts failed: {result.errors}")
    
    def _get_fallback_chain(self, failed_provider: Optional[ProviderType]) -> List[ProviderType]:
        if self._config.fallback_chain:
            chain = list(self._config.fallback_chain)
            if failed_provider in chain:
                chain.remove(failed_provider)
            return chain
        
        # Auto-generate chain from available providers
        available = self._registry.get_by_priority()
        chain = [p.provider_type for p in available]
        
        if failed_provider in chain:
            chain.remove(failed_provider)
        
        return chain
    
    def should_trigger(self, trigger: FallbackTrigger) -> bool:
        return trigger in self._config.triggers
    
    def record_failure(self, provider_type: ProviderType) -> None:
        self._failure_counts[provider_type] = self._failure_counts.get(provider_type, 0) + 1
    
    def reset_failures(self, provider_type: ProviderType) -> None:
        self._failure_counts[provider_type] = 0
