"""Context compression for efficient memory usage.

Part of Phase 2: Memory System Architecture
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from .context_window import ContextEntry, ContextPriority, ContextRole

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of a compression operation."""

    original_tokens: int
    compressed_tokens: int
    ratio: float
    entries_merged: int
    duration_ms: float = 0.0

    @property
    def savings(self) -> int:
        return self.original_tokens - self.compressed_tokens


class ContextCompressor:
    """Compresses context to fit within token limits."""

    def __init__(
        self,
        summarize_fn: Callable[[str], str] | None = None,
        target_ratio: float = 0.5,
    ):
        self._summarize = summarize_fn or self._default_summarize
        self._target_ratio = target_ratio

    def compress(
        self, entries: list[ContextEntry], target_tokens: int
    ) -> tuple[list[ContextEntry], CompressionResult]:
        start = datetime.utcnow()
        original_tokens = sum(e.token_count for e in entries)

        if original_tokens <= target_tokens:
            return entries, CompressionResult(
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                ratio=1.0,
                entries_merged=0,
            )

        compressed, merged = self._compress_entries(entries, target_tokens)
        compressed_tokens = sum(e.token_count for e in compressed)

        duration = (datetime.utcnow() - start).total_seconds() * 1000
        return compressed, CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            ratio=compressed_tokens / original_tokens if original_tokens else 1.0,
            entries_merged=merged,
            duration_ms=duration,
        )

    def _compress_entries(
        self, entries: list[ContextEntry], target: int
    ) -> tuple[list[ContextEntry], int]:
        pinned = [e for e in entries if e.pinned or e.role == ContextRole.SYSTEM]
        compressible = [
            e for e in entries if not e.pinned and e.role != ContextRole.SYSTEM
        ]

        pinned_tokens = sum(e.token_count for e in pinned)
        available = target - pinned_tokens

        if available <= 0:
            return pinned, len(compressible)

        # Group consecutive messages by role and summarize
        groups = self._group_by_role(compressible)
        compressed_groups = []
        merged_count = 0

        for role, group in groups:
            if len(group) > 1:
                merged_content = self._merge_and_summarize(group)
                import uuid

                compressed_groups.append(
                    ContextEntry(
                        id=str(uuid.uuid4()),
                        role=role,
                        content=merged_content,
                        token_count=len(merged_content.split()) * 2,  # Rough estimate
                        priority=ContextPriority.NORMAL,
                    )
                )
                merged_count += len(group) - 1
            else:
                compressed_groups.extend(group)

        return pinned + compressed_groups, merged_count

    def _group_by_role(
        self, entries: list[ContextEntry]
    ) -> list[tuple[ContextRole, list[ContextEntry]]]:
        if not entries:
            return []

        groups = []
        current_role = entries[0].role
        current_group = [entries[0]]

        for entry in entries[1:]:
            if entry.role == current_role:
                current_group.append(entry)
            else:
                groups.append((current_role, current_group))
                current_role = entry.role
                current_group = [entry]

        groups.append((current_role, current_group))
        return groups

    def _merge_and_summarize(self, entries: list[ContextEntry]) -> str:
        combined = "\n".join(e.content for e in entries)
        return self._summarize(combined)

    @staticmethod
    def _default_summarize(text: str) -> str:
        """Simple truncation-based summarization."""
        sentences = text.split(". ")
        if len(sentences) <= 3:
            return text
        return ". ".join(sentences[:2] + ["..."] + sentences[-1:])
