"""Stream handler for async LLM responses.

Part of Phase 2: LLM Architecture
"""

import logging
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..types import FinishReason, LLMResponse, StreamChunk

logger = logging.getLogger(__name__)


class StreamState(Enum):
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class StreamMetrics:
    """Metrics for a stream."""

    start_time: datetime = field(default_factory=datetime.utcnow)
    first_chunk_time: datetime | None = None
    end_time: datetime | None = None
    chunk_count: int = 0
    total_chars: int = 0

    @property
    def time_to_first_chunk_ms(self) -> float:
        if not self.first_chunk_time:
            return 0.0
        return (self.first_chunk_time - self.start_time).total_seconds() * 1000

    @property
    def total_duration_ms(self) -> float:
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds() * 1000


class StreamHandler:
    """Handles streaming LLM responses with callbacks."""

    def __init__(
        self,
        on_chunk: Callable[[StreamChunk], None] | None = None,
        on_complete: Callable[[str], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ):
        self._on_chunk = on_chunk
        self._on_complete = on_complete
        self._on_error = on_error
        self._state = StreamState.PENDING
        self._content = ""
        self._chunks: list[StreamChunk] = []
        self._metrics = StreamMetrics()
        self._cancelled = False

    @property
    def state(self) -> StreamState:
        return self._state

    @property
    def content(self) -> str:
        return self._content

    @property
    def metrics(self) -> StreamMetrics:
        return self._metrics

    async def handle(self, stream: AsyncIterator[StreamChunk]) -> str:
        """Process a stream and accumulate content."""
        self._state = StreamState.STREAMING
        self._metrics.start_time = datetime.utcnow()

        try:
            async for chunk in stream:
                if self._cancelled:
                    self._state = StreamState.CANCELLED
                    break

                if self._metrics.chunk_count == 0:
                    self._metrics.first_chunk_time = datetime.utcnow()

                self._chunks.append(chunk)
                self._content += chunk.delta
                self._metrics.chunk_count += 1
                self._metrics.total_chars += len(chunk.delta)

                if self._on_chunk:
                    self._on_chunk(chunk)

                if chunk.is_final:
                    break

            self._metrics.end_time = datetime.utcnow()
            self._state = StreamState.COMPLETED

            if self._on_complete:
                self._on_complete(self._content)

            return self._content

        except Exception as e:
            self._state = StreamState.ERROR
            logger.error("Stream error: %s", e)
            if self._on_error:
                self._on_error(e)
            raise

    def cancel(self) -> None:
        """Cancel the stream."""
        self._cancelled = True

    def to_response(self, model: str, provider: str) -> LLMResponse:
        """Convert accumulated stream to LLMResponse."""
        import uuid

        return LLMResponse(
            id=str(uuid.uuid4()),
            model=model,
            provider=provider,
            content=self._content,
            finish_reason=FinishReason.STOP,
            latency_ms=self._metrics.total_duration_ms,
        )
