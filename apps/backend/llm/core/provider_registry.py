"""Provider registry for LLM providers.

Part of Phase 2: LLM Architecture
"""

import logging
from typing import Dict, List, Optional, Type, TYPE_CHECKING
from datetime import datetime
import threading

from ..types import ProviderType, ProviderConfig, ProviderStatus

if TYPE_CHECKING:
    from ..providers import BaseLLMProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for LLM provider instances."""
    
    def __init__(self):
        self._providers: Dict[ProviderType, "BaseLLMProvider"] = {}
        self._configs: Dict[ProviderType, ProviderConfig] = {}
        self._factory: Dict[ProviderType, Type["BaseLLMProvider"]] = {}
        self._health: Dict[ProviderType, ProviderStatus] = {}
        self._lock = threading.RLock()
    
    def register_factory(self, provider_type: ProviderType, factory: Type["BaseLLMProvider"]) -> None:
        with self._lock:
            self._factory[provider_type] = factory
            logger.info("Registered factory for %s", provider_type.value)
    
    def register(self, config: ProviderConfig) -> None:
        with self._lock:
            self._configs[config.provider_type] = config
            self._health[config.provider_type] = ProviderStatus.UNKNOWN
            
            if config.provider_type in self._factory:
                self._providers[config.provider_type] = self._factory[config.provider_type](config)
                logger.info("Instantiated provider %s", config.provider_type.value)
    
    def get(self, provider_type: ProviderType) -> Optional["BaseLLMProvider"]:
        return self._providers.get(provider_type)
    
    def get_config(self, provider_type: ProviderType) -> Optional[ProviderConfig]:
        return self._configs.get(provider_type)
    
    def get_healthy(self) -> List["BaseLLMProvider"]:
        with self._lock:
            return [
                p for pt, p in self._providers.items()
                if self._health.get(pt) in (ProviderStatus.HEALTHY, ProviderStatus.UNKNOWN)
                and self._configs.get(pt, ProviderConfig(provider_type=pt)).enabled
            ]
    
    def get_by_priority(self) -> List["BaseLLMProvider"]:
        with self._lock:
            sorted_types = sorted(
                self._configs.keys(),
                key=lambda pt: self._configs[pt].priority,
                reverse=True
            )
            return [self._providers[pt] for pt in sorted_types if pt in self._providers]
    
    def update_health(self, provider_type: ProviderType, status: ProviderStatus) -> None:
        with self._lock:
            self._health[provider_type] = status
            logger.debug("Updated health for %s: %s", provider_type.value, status.value)
    
    def list_providers(self) -> List[ProviderType]:
        return list(self._providers.keys())
    
    def is_available(self, provider_type: ProviderType) -> bool:
        with self._lock:
            return (
                provider_type in self._providers
                and self._health.get(provider_type) != ProviderStatus.UNAVAILABLE
                and self._configs.get(provider_type, ProviderConfig(provider_type=provider_type)).enabled
            )
