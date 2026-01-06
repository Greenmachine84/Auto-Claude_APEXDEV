"""Sliding context window management.

Part of Phase 2: Memory System Architecture
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContextRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContextPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class ContextEntry:
    """A single entry in the context window."""
    id: str
    role: ContextRole
    content: str
    priority: ContextPriority = ContextPriority.NORMAL
    token_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    pinned: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "role": self.role.value, "content": self.content,
            "priority": self.priority.value, "token_count": self.token_count,
            "created_at": self.created_at.isoformat(), "pinned": self.pinned
        }


class ContextWindow:
    """Manages a sliding context window with priority-based truncation."""
    
    def __init__(self, max_tokens: int = 8000, reserve_tokens: int = 1000):
        self._max_tokens = max_tokens
        self._reserve = reserve_tokens
        self._entries: List[ContextEntry] = []
        self._total_tokens = 0
    
    def add(self, entry: ContextEntry) -> bool:
        if entry.token_count > self._max_tokens:
            logger.warning("Entry too large: %d tokens", entry.token_count)
            return False
        
        self._entries.append(entry)
        self._total_tokens += entry.token_count
        
        while self._total_tokens > self._max_tokens - self._reserve:
            if not self._evict_lowest_priority():
                break
        
        return True
    
    def get_messages(self) -> List[Dict[str, str]]:
        return [{"role": e.role.value, "content": e.content} for e in self._entries]
    
    def get_entries(self) -> List[ContextEntry]:
        return list(self._entries)
    
    def clear(self) -> int:
        count = len(self._entries)
        self._entries.clear()
        self._total_tokens = 0
        return count
    
    def pin(self, entry_id: str) -> bool:
        for entry in self._entries:
            if entry.id == entry_id:
                entry.pinned = True
                return True
        return False
    
    def unpin(self, entry_id: str) -> bool:
        for entry in self._entries:
            if entry.id == entry_id:
                entry.pinned = False
                return True
        return False
    
    def available_tokens(self) -> int:
        return max(0, self._max_tokens - self._reserve - self._total_tokens)
    
    def total_tokens(self) -> int:
        return self._total_tokens
    
    def _evict_lowest_priority(self) -> bool:
        evict_candidates = [
            (i, e) for i, e in enumerate(self._entries)
            if not e.pinned and e.role != ContextRole.SYSTEM
        ]
        
        if not evict_candidates:
            return False
        
        evict_candidates.sort(key=lambda x: (x[1].priority.value, x[1].created_at), reverse=True)
        idx, entry = evict_candidates[0]
        
        self._entries.pop(idx)
        self._total_tokens -= entry.token_count
        logger.debug("Evicted entry %s (priority=%s)", entry.id, entry.priority.value)
        return True
