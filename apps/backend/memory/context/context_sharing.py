"""Cross-agent context sharing.

Part of Phase 2: Memory System Architecture
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .context_window import ContextEntry, ContextRole, ContextPriority

logger = logging.getLogger(__name__)


@dataclass
class SharedContext:
    """Context shared between agents."""
    id: str
    source_agent: str
    content: str
    context_type: str  # "finding", "decision", "knowledge", "state"
    priority: ContextPriority = ContextPriority.NORMAL
    subscribers: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_entry(self) -> ContextEntry:
        return ContextEntry(
            id=self.id, role=ContextRole.SYSTEM, content=f"[Shared:{self.context_type}] {self.content}",
            priority=self.priority, metadata={"source_agent": self.source_agent, **self.metadata}
        )


class ContextBroker:
    """Broker for sharing context between agents."""
    
    _instance: Optional["ContextBroker"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "ContextBroker":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._shared: Dict[str, SharedContext] = {}
                    cls._instance._subscriptions: Dict[str, Set[str]] = {}  # agent_id -> context_ids
        return cls._instance
    
    def share(self, context: SharedContext) -> str:
        self._shared[context.id] = context
        
        for subscriber in context.subscribers:
            if subscriber not in self._subscriptions:
                self._subscriptions[subscriber] = set()
            self._subscriptions[subscriber].add(context.id)
        
        logger.info("Shared context %s from %s to %d subscribers", 
                   context.id, context.source_agent, len(context.subscribers))
        return context.id
    
    def subscribe(self, agent_id: str, context_id: str) -> bool:
        if context_id not in self._shared:
            return False
        
        self._shared[context_id].subscribers.add(agent_id)
        if agent_id not in self._subscriptions:
            self._subscriptions[agent_id] = set()
        self._subscriptions[agent_id].add(context_id)
        return True
    
    def unsubscribe(self, agent_id: str, context_id: str) -> bool:
        if context_id in self._shared:
            self._shared[context_id].subscribers.discard(agent_id)
        if agent_id in self._subscriptions:
            self._subscriptions[agent_id].discard(context_id)
        return True
    
    def get_for_agent(self, agent_id: str) -> List[SharedContext]:
        context_ids = self._subscriptions.get(agent_id, set())
        contexts = []
        
        now = datetime.utcnow()
        for cid in context_ids:
            ctx = self._shared.get(cid)
            if ctx and (ctx.expires_at is None or ctx.expires_at > now):
                contexts.append(ctx)
        
        return sorted(contexts, key=lambda c: c.priority.value)
    
    def broadcast(self, source_agent: str, content: str, context_type: str, 
                  target_agents: Optional[List[str]] = None) -> str:
        shared = SharedContext(
            id=str(uuid.uuid4()), source_agent=source_agent, content=content,
            context_type=context_type, subscribers=set(target_agents or [])
        )
        return self.share(shared)
    
    def revoke(self, context_id: str) -> bool:
        if context_id not in self._shared:
            return False
        
        context = self._shared.pop(context_id)
        for subscriber in context.subscribers:
            if subscriber in self._subscriptions:
                self._subscriptions[subscriber].discard(context_id)
        
        return True
    
    def clear(self) -> int:
        count = len(self._shared)
        self._shared.clear()
        self._subscriptions.clear()
        return count
