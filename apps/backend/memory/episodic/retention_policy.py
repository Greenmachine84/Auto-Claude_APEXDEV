"""Retention policy management for episode cleanup.

Part of Phase 2: Memory System Architecture
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from ..types.episode_types import EpisodeRecord, EpisodeSeverity

logger = logging.getLogger(__name__)


class RetentionAction(Enum):
    KEEP = "keep"
    ARCHIVE = "archive"
    DELETE = "delete"


@dataclass
class RetentionResult:
    """Result of retention policy execution."""
    kept: int = 0
    archived: int = 0
    deleted: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {"kept": self.kept, "archived": self.archived, 
                "deleted": self.deleted, "errors": self.errors,
                "duration_ms": self.duration_ms}


@dataclass
class RetentionRule:
    """A single retention rule."""
    name: str
    condition: str  # "age", "count", "severity"
    threshold: Any
    action: RetentionAction
    priority: int = 0


class RetentionPolicy:
    """Manage episode retention based on configurable rules."""
    
    def __init__(
        self,
        max_age_days: int = 90,
        max_per_agent: int = 1000,
        preserve_critical: bool = True
    ):
        self._max_age = timedelta(days=max_age_days)
        self._max_per_agent = max_per_agent
        self._preserve_critical = preserve_critical
        self._rules: List[RetentionRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        self._rules = [
            RetentionRule("preserve_critical", "severity", EpisodeSeverity.CRITICAL, RetentionAction.KEEP, 100),
            RetentionRule("delete_old", "age", self._max_age, RetentionAction.DELETE, 10),
            RetentionRule("archive_stale", "age", self._max_age / 2, RetentionAction.ARCHIVE, 5),
        ]
    
    def add_rule(self, rule: RetentionRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
    
    def evaluate(self, episode: EpisodeRecord, agent_episode_count: int = 0) -> RetentionAction:
        now = datetime.utcnow()
        age = now - episode.created_at
        
        if self._preserve_critical and episode.severity == EpisodeSeverity.CRITICAL:
            return RetentionAction.KEEP
        
        for rule in self._rules:
            if rule.condition == "severity" and episode.severity == rule.threshold:
                return rule.action
            elif rule.condition == "age" and age > rule.threshold:
                return rule.action
            elif rule.condition == "count" and agent_episode_count > rule.threshold:
                return rule.action
        
        return RetentionAction.KEEP
    
    def apply(self, episodes: List[EpisodeRecord], agent_counts: Dict[str, int]) -> RetentionResult:
        start = datetime.utcnow()
        result = RetentionResult()
        
        for ep in episodes:
            try:
                action = self.evaluate(ep, agent_counts.get(ep.agent_id, 0))
                if action == RetentionAction.KEEP:
                    result.kept += 1
                elif action == RetentionAction.ARCHIVE:
                    result.archived += 1
                else:
                    result.deleted += 1
            except Exception as e:
                result.errors.append(f"Error evaluating {ep.id}: {e}")
        
        result.duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        return result
