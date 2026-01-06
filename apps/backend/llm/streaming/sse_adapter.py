"""Server-Sent Events adapter.

Part of Phase 2: LLM Architecture
"""

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..types import StreamChunk, FinishReason

logger = logging.getLogger(__name__)


@dataclass
class SSEEvent:
    """A Server-Sent Event."""
    data: str
    event: str = "message"
    id: Optional[str] = None
    retry: Optional[int] = None
    
    def encode(self) -> str:
        """Encode to SSE format."""
        lines = []
        if self.id:
            lines.append(f"id: {self.id}")
        if self.event != "message":
            lines.append(f"event: {self.event}")
        if self.retry:
            lines.append(f"retry: {self.retry}")
        for line in self.data.split("\n"):
            lines.append(f"data: {line}")
        lines.append("")
        return "\n".join(lines) + "\n"
    
    @classmethod
    def from_chunk(cls, chunk: StreamChunk, event_id: Optional[str] = None) -> "SSEEvent":
        """Create SSE event from StreamChunk."""
        data = json.dumps({
            "content": chunk.content,
            "delta": chunk.delta,
            "finish_reason": chunk.finish_reason.value if chunk.finish_reason else None
        })
        return cls(data=data, event="chunk", id=event_id)


class SSEAdapter:
    """Adapts LLM streams to Server-Sent Events."""
    
    def __init__(self, heartbeat_interval: float = 15.0):
        self._heartbeat_interval = heartbeat_interval
        self._event_counter = 0
    
    async def adapt(self, stream: AsyncIterator[StreamChunk]) -> AsyncIterator[str]:
        """Convert stream chunks to SSE strings."""
        try:
            async for chunk in stream:
                self._event_counter += 1
                event = SSEEvent.from_chunk(chunk, event_id=str(self._event_counter))
                yield event.encode()
                
                if chunk.is_final:
                    done_event = SSEEvent(data="[DONE]", event="done")
                    yield done_event.encode()
                    break
        
        except Exception as e:
            error_event = SSEEvent(
                data=json.dumps({"error": str(e)}),
                event="error"
            )
            yield error_event.encode()
    
    async def adapt_with_heartbeat(self, stream: AsyncIterator[StreamChunk]) -> AsyncIterator[str]:
        """Convert stream chunks to SSE with heartbeats."""
        heartbeat_task = None
        queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        
        async def producer():
            try:
                async for chunk in stream:
                    self._event_counter += 1
                    event = SSEEvent.from_chunk(chunk, event_id=str(self._event_counter))
                    await queue.put(event.encode())
                    
                    if chunk.is_final:
                        await queue.put(SSEEvent(data="[DONE]", event="done").encode())
                        break
            finally:
                await queue.put(None)
        
        async def heartbeat():
            while True:
                await asyncio.sleep(self._heartbeat_interval)
                await queue.put(SSEEvent(data="", event="heartbeat").encode())
        
        producer_task = asyncio.create_task(producer())
        heartbeat_task = asyncio.create_task(heartbeat())
        
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
    
    @staticmethod
    def parse_sse(line: str) -> Optional[SSEEvent]:
        """Parse a single SSE line."""
        if not line or line.startswith(":"):
            return None
        
        if line.startswith("data: "):
            return SSEEvent(data=line[6:])
        
        return None
