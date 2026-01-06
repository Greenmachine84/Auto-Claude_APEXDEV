"""Relevance scorer for context items.

Part of Phase 2: Memory System Architecture
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, TypeVar
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class Task:
    """Task representation for relevance scoring."""
    id: str
    description: str
    keywords: List[str]
    agent_type: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ScoredItem:
    """An item with its relevance score."""
    item: Any
    score: float
    factors: Dict[str, float]


class RelevanceScorer:
    """Score context items by relevance to current task.
    
    Uses multiple factors:
    - Keyword matching
    - Recency
    - Success history (for episodes)
    - Agent type matching
    """
    
    def __init__(
        self,
        keyword_weight: float = 0.4,
        recency_weight: float = 0.3,
        success_weight: float = 0.2,
        agent_weight: float = 0.1
    ):
        self._weights = {
            "keyword": keyword_weight,
            "recency": recency_weight,
            "success": success_weight,
            "agent": agent_weight
        }
    
    def score(self, context_item: Any, task: Task) -> float:
        """Score a single context item against a task."""
        factors = self._compute_factors(context_item, task)
        total = sum(
            factors.get(k, 0.0) * w 
            for k, w in self._weights.items()
        )
        return min(1.0, max(0.0, total))
    
    def rank(self, items: List[Any], task: Task) -> List[ScoredItem]:
        """Rank items by relevance to task."""
        scored = []
        for item in items:
            factors = self._compute_factors(item, task)
            total = sum(
                factors.get(k, 0.0) * w 
                for k, w in self._weights.items()
            )
            scored.append(ScoredItem(
                item=item,
                score=min(1.0, max(0.0, total)),
                factors=factors
            ))
        
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored
    
    def _compute_factors(self, item: Any, task: Task) -> Dict[str, float]:
        """Compute individual scoring factors."""
        factors = {}
        
        # Keyword matching
        item_text = self._extract_text(item).lower()
        if task.keywords:
            matches = sum(
                1 for kw in task.keywords 
                if kw.lower() in item_text
            )
            factors["keyword"] = min(1.0, matches / len(task.keywords))
        else:
            # Fallback: check description words
            desc_words = set(re.findall(r'\w+', task.description.lower()))
            item_words = set(re.findall(r'\w+', item_text))
            if desc_words:
                overlap = len(desc_words & item_words) / len(desc_words)
                factors["keyword"] = min(1.0, overlap * 2)
        
        # Recency
        item_time = self._extract_time(item)
        if item_time:
            age = datetime.utcnow() - item_time
            # Full score if within 1 hour, decay over 7 days
            if age < timedelta(hours=1):
                factors["recency"] = 1.0
            elif age < timedelta(days=7):
                factors["recency"] = 1.0 - (age.days / 7.0)
            else:
                factors["recency"] = 0.1
        else:
            factors["recency"] = 0.5  # Unknown recency
        
        # Success (for episodes)
        success = self._extract_success(item)
        if success is not None:
            factors["success"] = 1.0 if success else 0.3
        else:
            factors["success"] = 0.5
        
        # Agent type matching
        item_agent = self._extract_agent(item)
        if item_agent and task.agent_type:
            factors["agent"] = 1.0 if item_agent == task.agent_type else 0.5
        else:
            factors["agent"] = 0.5
        
        return factors
    
    def _extract_text(self, item: Any) -> str:
        """Extract searchable text from item."""
        if hasattr(item, 'text'):
            return str(item.text)
        if hasattr(item, 'input_text'):
            return f"{item.input_text} {getattr(item, 'output_text', '')}"
        if hasattr(item, 'content'):
            return str(item.content)
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            return " ".join(str(v) for v in item.values())
        return str(item)
    
    def _extract_time(self, item: Any) -> Optional[datetime]:
        """Extract timestamp from item."""
        for attr in ('created_at', 'timestamp', 'time', 'date'):
            if hasattr(item, attr):
                val = getattr(item, attr)
                if isinstance(val, datetime):
                    return val
        if isinstance(item, dict):
            for key in ('created_at', 'timestamp', 'time'):
                if key in item and isinstance(item[key], datetime):
                    return item[key]
        return None
    
    def _extract_success(self, item: Any) -> Optional[bool]:
        """Extract success status from item."""
        if hasattr(item, 'success'):
            return bool(item.success)
        if isinstance(item, dict) and 'success' in item:
            return bool(item['success'])
        return None
    
    def _extract_agent(self, item: Any) -> Optional[str]:
        """Extract agent type from item."""
        if hasattr(item, 'agent_id'):
            return str(item.agent_id)
        if hasattr(item, 'agent_type'):
            return str(item.agent_type)
        if isinstance(item, dict):
            return item.get('agent_id') or item.get('agent_type')
        return None
