"""Reflexion pattern extraction for learning from episodes.

Part of Phase 2: Memory System Architecture
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..types.episode_types import EpisodeRecord, EpisodeOutcome


class LessonType(Enum):
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_AVOIDANCE = "failure_avoidance"
    TOOL_USAGE = "tool_usage"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class LessonLearned:
    """A lesson extracted from episode analysis."""
    id: str
    lesson_type: LessonType
    title: str
    description: str
    source_episodes: List[str]
    confidence: float
    applicability: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "lesson_type": self.lesson_type.value,
            "title": self.title, "description": self.description,
            "source_episodes": self.source_episodes, "confidence": self.confidence,
            "applicability": self.applicability,
            "created_at": self.created_at.isoformat(), "metadata": self.metadata
        }


class ReflexionExtractor:
    """Extract lessons from episode patterns."""
    
    def __init__(self, min_episodes: int = 3, confidence_threshold: float = 0.7):
        self._min_episodes = min_episodes
        self._confidence_threshold = confidence_threshold
        self._lessons: Dict[str, LessonLearned] = {}
    
    def analyze_success_patterns(self, episodes: List[EpisodeRecord]) -> List[LessonLearned]:
        successful = [e for e in episodes if e.outcome == EpisodeOutcome.SUCCESS]
        if len(successful) < self._min_episodes:
            return []
        
        lessons = []
        tool_patterns = self._extract_tool_patterns(successful)
        for pattern, count in tool_patterns.items():
            if count >= self._min_episodes:
                import uuid
                lesson = LessonLearned(
                    id=str(uuid.uuid4()), lesson_type=LessonType.SUCCESS_PATTERN,
                    title=f"Effective tool combination: {pattern}",
                    description=f"Using {pattern} led to success in {count} episodes",
                    source_episodes=[e.id for e in successful[:5]],
                    confidence=min(0.95, 0.5 + (count / len(episodes)) * 0.5)
                )
                lessons.append(lesson)
        return lessons
    
    def analyze_failure_patterns(self, episodes: List[EpisodeRecord]) -> List[LessonLearned]:
        failed = [e for e in episodes if e.outcome in (EpisodeOutcome.FAILURE, EpisodeOutcome.ERROR)]
        if len(failed) < self._min_episodes:
            return []
        
        lessons = []
        error_patterns = self._extract_error_patterns(failed)
        for pattern, data in error_patterns.items():
            if data["count"] >= 2:
                import uuid
                lesson = LessonLearned(
                    id=str(uuid.uuid4()), lesson_type=LessonType.FAILURE_AVOIDANCE,
                    title=f"Avoid: {pattern[:50]}",
                    description=f"This pattern led to failure {data['count']} times",
                    source_episodes=data["episodes"][:3],
                    confidence=min(0.9, 0.4 + (data["count"] / len(episodes)) * 0.5)
                )
                lessons.append(lesson)
        return lessons
    
    def _extract_tool_patterns(self, episodes: List[EpisodeRecord]) -> Dict[str, int]:
        patterns: Dict[str, int] = {}
        for ep in episodes:
            key = ",".join(sorted(ep.tools_used))
            patterns[key] = patterns.get(key, 0) + 1
        return patterns
    
    def _extract_error_patterns(self, episodes: List[EpisodeRecord]) -> Dict[str, Dict[str, Any]]:
        patterns: Dict[str, Dict[str, Any]] = {}
        for ep in episodes:
            for inv in ep.tool_invocations:
                if not inv.success and inv.error_message:
                    key = inv.error_message[:100]
                    if key not in patterns:
                        patterns[key] = {"count": 0, "episodes": []}
                    patterns[key]["count"] += 1
                    patterns[key]["episodes"].append(ep.id)
        return patterns
