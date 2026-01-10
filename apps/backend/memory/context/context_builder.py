"""Context builder for LLM calls.

Part of Phase 2: Memory System Architecture
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from ..episodic.episode_record import EpisodeRecord

logger = logging.getLogger(__name__)


@dataclass
class Context:
    """Built context ready for LLM consumption."""

    text: str
    token_count: int
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A search result from semantic memory."""

    id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextBuilder:
    """Fluent builder for constructing LLM context.

    Combines episodes, semantic search results, and files
    into a coherent context that fits within token limits.
    """

    def __init__(self, max_tokens: int = 8000):
        self._max_tokens = max_tokens
        self._episodes: list[EpisodeRecord] = []
        self._semantic_results: list[SearchResult] = []
        self._files: dict[str, str] = {}
        self._system_context: str = ""
        self._priority_texts: list[str] = []

    def with_episodes(self, episodes: list[EpisodeRecord]) -> "ContextBuilder":
        """Add episodes to context."""
        self._episodes.extend(episodes)
        return self

    def with_semantic_results(self, results: list[SearchResult]) -> "ContextBuilder":
        """Add semantic search results to context."""
        self._semantic_results.extend(results)
        return self

    def with_files(self, file_contents: dict[str, str]) -> "ContextBuilder":
        """Add file contents to context."""
        self._files.update(file_contents)
        return self

    def with_system_context(self, text: str) -> "ContextBuilder":
        """Add system-level context (always included first)."""
        self._system_context = text
        return self

    def with_priority(self, text: str) -> "ContextBuilder":
        """Add priority text that should be included first."""
        self._priority_texts.append(text)
        return self

    def build(self, max_tokens: int | None = None) -> Context:
        """Build the context, fitting within token limits."""
        limit = max_tokens or self._max_tokens
        parts = []
        sources = []

        # System context first (always included)
        if self._system_context:
            parts.append(self._system_context)
            sources.append("system")

        # Priority texts next
        for text in self._priority_texts:
            parts.append(text)
            sources.append("priority")

        # Episodes (most recent first, most relevant)
        if self._episodes:
            episode_text = self._format_episodes()
            parts.append(episode_text)
            sources.append(f"episodes:{len(self._episodes)}")

        # Semantic results (by relevance score)
        if self._semantic_results:
            semantic_text = self._format_semantic_results()
            parts.append(semantic_text)
            sources.append(f"semantic:{len(self._semantic_results)}")

        # Files (if space permits)
        if self._files:
            file_text = self._format_files()
            parts.append(file_text)
            sources.append(f"files:{len(self._files)}")

        full_text = "\n\n".join(parts)
        token_count = self._estimate_tokens(full_text)

        # Truncate if needed
        if token_count > limit:
            full_text = self._truncate_to_limit(full_text, limit)
            token_count = limit

        return Context(text=full_text, token_count=token_count, sources=sources)

    def _format_episodes(self) -> str:
        """Format episodes for context."""
        lines = ["## Relevant Episodes"]
        for ep in self._episodes[-5:]:  # Last 5 most recent
            status = "Success" if ep.success else "Failed"
            lines.append(f"### [{status}] {ep.agent_id}")
            lines.append(f"Input: {ep.input_text[:200]}")
            lines.append(f"Output: {ep.output_text[:500]}")
            if ep.tools_used:
                lines.append(f"Tools: {', '.join(ep.tools_used)}")
            lines.append("")
        return "\n".join(lines)

    def _format_semantic_results(self) -> str:
        """Format semantic results for context."""
        lines = ["## Relevant Knowledge"]
        for result in self._semantic_results[:10]:  # Top 10
            lines.append(f"[score={result.score:.2f}] {result.text}")
        return "\n".join(lines)

    def _format_files(self) -> str:
        """Format files for context."""
        lines = ["## Files"]
        for path, content in self._files.items():
            lines.append(f"### {path}")
            lines.append("```")
            lines.append(content[:2000])  # Limit per file
            lines.append("```")
        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 4 chars per token)."""
        return len(text) // 4

    def _truncate_to_limit(self, text: str, limit: int) -> str:
        """Truncate text to fit token limit."""
        char_limit = limit * 4
        if len(text) <= char_limit:
            return text
        return text[: char_limit - 20] + "\n... [truncated]"
