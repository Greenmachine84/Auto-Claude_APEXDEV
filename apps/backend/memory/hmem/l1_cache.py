"""L1 in-memory cache tier.

Part of Phase 2: Memory System Architecture
"""

import logging
import threading
from typing import Dict, Generic, Optional, TypeVar
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Entry in L1 cache with TTL."""
    value: T
    created_at: datetime
    expires_at: datetime
    access_count: int = 0


class L1Cache(Generic[T]):
    """LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._max_size = max_size
        self._ttl = timedelta(seconds=ttl_seconds)
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            now = datetime.utcnow()
            if now > entry.expires_at:
                del self._cache[key]
                return None
            
            entry.access_count += 1
            self._cache.move_to_end(key)
            return entry.value
    
    def set(self, key: str, value: T) -> None:
        with self._lock:
            now = datetime.utcnow()
            
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = CacheEntry(
                value=value, created_at=now, expires_at=now + self._ttl
            )
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def size(self) -> int:
        return len(self._cache)
    
    def evict_expired(self) -> int:
        with self._lock:
            now = datetime.utcnow()
            expired = [k for k, v in self._cache.items() if now > v.expires_at]
            for key in expired:
                del self._cache[key]
            return len(expired)
