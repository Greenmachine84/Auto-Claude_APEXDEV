"""L2 session storage tier.

Part of Phase 2: Memory System Architecture
"""

import logging
import threading
from typing import Dict, Generic, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class SessionEntry(Generic[T]):
    """Entry in L2 session storage."""
    value: T
    session_id: str
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    metadata: Dict = field(default_factory=dict)


class L2SessionStore(Generic[T]):
    """Session-scoped storage with configurable TTL."""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self._max_size = max_size
        self._ttl = timedelta(seconds=ttl_seconds)
        self._store: Dict[str, SessionEntry[T]] = {}
        self._lock = threading.RLock()
        self._current_session: str = "default"
    
    def set_session(self, session_id: str) -> None:
        self._current_session = session_id
    
    def get(self, key: str) -> Optional[T]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            
            now = datetime.utcnow()
            if now > entry.expires_at:
                del self._store[key]
                return None
            
            entry.access_count += 1
            return entry.value
    
    def set(self, key: str, value: T, metadata: Optional[Dict] = None) -> None:
        with self._lock:
            now = datetime.utcnow()
            
            if len(self._store) >= self._max_size and key not in self._store:
                self._evict_oldest()
            
            self._store[key] = SessionEntry(
                value=value, session_id=self._current_session,
                created_at=now, expires_at=now + self._ttl,
                metadata=metadata or {}
            )
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False
    
    def clear(self) -> int:
        with self._lock:
            count = len(self._store)
            self._store.clear()
            return count
    
    def clear_session(self, session_id: str) -> int:
        with self._lock:
            keys = [k for k, v in self._store.items() if v.session_id == session_id]
            for key in keys:
                del self._store[key]
            return len(keys)
    
    def size(self) -> int:
        return len(self._store)
    
    def _evict_oldest(self) -> None:
        if not self._store:
            return
        oldest_key = min(self._store.keys(), key=lambda k: self._store[k].created_at)
        del self._store[oldest_key]
