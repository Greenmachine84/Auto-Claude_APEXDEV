"""Tier manager for H-MEM hierarchical memory.

Part of Phase 2: Memory System Architecture
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from .l1_cache import L1Cache
from .l2_session import L2SessionStore
from .l3_persistent import L3PersistentStore
from .promotion import DemotionPolicy, PromotionPolicy

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MemoryTier(Enum):
    L1_CACHE = 1
    L2_SESSION = 2
    L3_PERSISTENT = 3


@dataclass
class TierConfig:
    """Configuration for tier management."""

    l1_max_items: int = 1000
    l1_ttl_seconds: int = 300
    l2_max_items: int = 10000
    l2_ttl_seconds: int = 3600
    l3_db_path: str = "data/memory/l3.db"
    auto_promote: bool = True
    auto_demote: bool = True


@dataclass
class TierStats:
    """Statistics for tier operations."""

    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    promotions: int = 0
    demotions: int = 0


class TierManager(Generic[T]):
    """Manages data flow across memory tiers."""

    def __init__(self, config: TierConfig | None = None):
        self._config = config or TierConfig()
        self._l1 = L1Cache[T](
            max_size=self._config.l1_max_items, ttl_seconds=self._config.l1_ttl_seconds
        )
        self._l2 = L2SessionStore[T](
            max_size=self._config.l2_max_items, ttl_seconds=self._config.l2_ttl_seconds
        )
        self._l3 = L3PersistentStore[T](db_path=self._config.l3_db_path)
        self._promotion = PromotionPolicy()
        self._demotion = DemotionPolicy()
        self._stats = TierStats()

    def get(self, key: str) -> T | None:
        # L1 lookup
        value = self._l1.get(key)
        if value is not None:
            self._stats.l1_hits += 1
            return value
        self._stats.l1_misses += 1

        # L2 lookup
        value = self._l2.get(key)
        if value is not None:
            self._stats.l2_hits += 1
            if self._config.auto_promote and self._promotion.should_promote(key):
                self._l1.set(key, value)
                self._stats.promotions += 1
            return value
        self._stats.l2_misses += 1

        # L3 lookup
        value = self._l3.get(key)
        if value is not None:
            self._stats.l3_hits += 1
            if self._config.auto_promote:
                self._l2.set(key, value)
                self._stats.promotions += 1
            return value
        self._stats.l3_misses += 1

        return None

    def set(self, key: str, value: T, tier: MemoryTier = MemoryTier.L1_CACHE) -> None:
        if tier == MemoryTier.L1_CACHE:
            self._l1.set(key, value)
        elif tier == MemoryTier.L2_SESSION:
            self._l2.set(key, value)
        else:
            self._l3.set(key, value)

    def delete(self, key: str) -> bool:
        deleted = False
        deleted = self._l1.delete(key) or deleted
        deleted = self._l2.delete(key) or deleted
        deleted = self._l3.delete(key) or deleted
        return deleted

    def demote(self, key: str) -> bool:
        # L1 -> L2
        value = self._l1.get(key)
        if value is not None:
            self._l2.set(key, value)
            self._l1.delete(key)
            self._stats.demotions += 1
            return True

        # L2 -> L3
        value = self._l2.get(key)
        if value is not None:
            self._l3.set(key, value)
            self._l2.delete(key)
            self._stats.demotions += 1
            return True

        return False

    def promote(self, key: str) -> bool:
        # L3 -> L2
        value = self._l3.get(key)
        if value is not None and self._l2.get(key) is None:
            self._l2.set(key, value)
            self._stats.promotions += 1
            return True

        # L2 -> L1
        value = self._l2.get(key)
        if value is not None and self._l1.get(key) is None:
            self._l1.set(key, value)
            self._stats.promotions += 1
            return True

        return False

    def get_stats(self) -> TierStats:
        return self._stats

    def clear_tier(self, tier: MemoryTier) -> int:
        if tier == MemoryTier.L1_CACHE:
            return self._l1.clear()
        elif tier == MemoryTier.L2_SESSION:
            return self._l2.clear()
        else:
            return self._l3.clear()
