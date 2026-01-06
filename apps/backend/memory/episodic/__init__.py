"""Episodic memory module - Episode storage and retrieval.

Provides SQLite-based persistent episode storage with:
- Full-text search (FTS5)
- Query builder pattern
- Reflexion pattern extraction
- Retention policies

Part of Phase 2: Memory System Architecture
"""

from .episode_store import EpisodeStore
from .episode_query import EpisodeQueryBuilder
from .reflexion_pattern import ReflexionExtractor, LessonLearned
from .retention_policy import RetentionPolicy, RetentionResult

__all__ = [
    "EpisodeStore",
    "EpisodeQueryBuilder",
    "ReflexionExtractor",
    "LessonLearned",
    "RetentionPolicy",
    "RetentionResult",
]
