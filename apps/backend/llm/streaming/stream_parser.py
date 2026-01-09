"""Stream parser for different streaming formats.

Part of Phase 2: LLM Architecture
"""

import json
import logging
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..types import FinishReason, StreamChunk, ToolCall

logger = logging.getLogger(__name__)


class StreamFormat(Enum):
    """Supported streaming formats."""

    SSE = "sse"  # Server-Sent Events
    JSONL = "jsonl"  # JSON Lines
    OPENAI = "openai"  # OpenAI streaming format
    ANTHROPIC = "anthropic"  # Anthropic streaming format
    OLLAMA = "ollama"  # Ollama streaming format


@dataclass
class ParsedEvent:
    """A parsed streaming event."""

    event_type: str
    data: dict[str, Any]
    raw: str


class StreamParser:
    """Parse streaming responses from various providers.

    Handles:
    - SSE (Server-Sent Events) format
    - JSON Lines format
    - Provider-specific formats (OpenAI, Anthropic, Ollama)
    """

    def __init__(self, format: StreamFormat = StreamFormat.SSE):
        self._format = format
        self._buffer = ""

    def parse_line(self, line: str) -> StreamChunk | None:
        """Parse a single line into a StreamChunk."""
        line = line.strip()
        if not line:
            return None

        if self._format == StreamFormat.SSE:
            return self._parse_sse_line(line)
        elif self._format == StreamFormat.JSONL:
            return self._parse_jsonl_line(line)
        elif self._format == StreamFormat.OPENAI:
            return self._parse_openai_line(line)
        elif self._format == StreamFormat.ANTHROPIC:
            return self._parse_anthropic_line(line)
        elif self._format == StreamFormat.OLLAMA:
            return self._parse_ollama_line(line)

        return None

    def parse_lines(self, lines: Iterator[str]) -> Iterator[StreamChunk]:
        """Parse multiple lines into StreamChunks."""
        for line in lines:
            chunk = self.parse_line(line)
            if chunk:
                yield chunk

    async def parse_async(
        self, lines: AsyncIterator[str]
    ) -> AsyncIterator[StreamChunk]:
        """Parse async line stream into StreamChunks."""
        async for line in lines:
            chunk = self.parse_line(line)
            if chunk:
                yield chunk

    def _parse_sse_line(self, line: str) -> StreamChunk | None:
        """Parse SSE format line."""
        if line.startswith(":"):
            # Comment/keep-alive
            return None

        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                return StreamChunk(
                    delta="", content="", is_final=True, finish_reason=FinishReason.STOP
                )

            try:
                parsed = json.loads(data)
                return self._extract_chunk(parsed)
            except json.JSONDecodeError:
                logger.debug("Failed to parse SSE data: %s", data[:100])

        return None

    def _parse_jsonl_line(self, line: str) -> StreamChunk | None:
        """Parse JSON Lines format."""
        try:
            parsed = json.loads(line)
            return self._extract_chunk(parsed)
        except json.JSONDecodeError:
            return None

    def _parse_openai_line(self, line: str) -> StreamChunk | None:
        """Parse OpenAI streaming format."""
        # OpenAI uses SSE with specific structure
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                return StreamChunk(
                    delta="", content="", is_final=True, finish_reason=FinishReason.STOP
                )

            try:
                parsed = json.loads(data)
                choices = parsed.get("choices", [])
                if choices:
                    choice = choices[0]
                    delta = choice.get("delta", {})

                    content = delta.get("content", "")
                    finish = choice.get("finish_reason")

                    tool_calls = []
                    if "tool_calls" in delta:
                        for tc in delta["tool_calls"]:
                            tool_calls.append(
                                ToolCall(
                                    id=tc.get("id", ""),
                                    name=tc.get("function", {}).get("name", ""),
                                    arguments=tc.get("function", {}).get(
                                        "arguments", ""
                                    ),
                                )
                            )

                    return StreamChunk(
                        delta=content,
                        content=content,
                        tool_calls=tool_calls,
                        is_final=finish is not None,
                        finish_reason=self._map_finish_reason(finish),
                    )
            except json.JSONDecodeError:
                pass

        return None

    def _parse_anthropic_line(self, line: str) -> StreamChunk | None:
        """Parse Anthropic streaming format."""
        if line.startswith("data: "):
            data = line[6:]
            try:
                parsed = json.loads(data)
                event_type = parsed.get("type", "")

                if event_type == "content_block_delta":
                    delta = parsed.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        return StreamChunk(delta=text, content=text)
                    elif delta.get("type") == "input_json_delta":
                        # Tool call argument streaming
                        return StreamChunk(
                            delta="",
                            content="",
                            tool_calls=[
                                ToolCall(
                                    id=parsed.get("index", ""),
                                    name="",
                                    arguments=delta.get("partial_json", ""),
                                )
                            ],
                        )

                elif event_type == "message_stop":
                    return StreamChunk(
                        delta="",
                        content="",
                        is_final=True,
                        finish_reason=FinishReason.STOP,
                    )

            except json.JSONDecodeError:
                pass

        return None

    def _parse_ollama_line(self, line: str) -> StreamChunk | None:
        """Parse Ollama streaming format."""
        try:
            parsed = json.loads(line)

            content = parsed.get("message", {}).get("content", "")
            if not content:
                content = parsed.get("response", "")

            done = parsed.get("done", False)

            return StreamChunk(
                delta=content,
                content=content,
                is_final=done,
                finish_reason=FinishReason.STOP if done else None,
            )
        except json.JSONDecodeError:
            return None

    def _extract_chunk(self, data: dict[str, Any]) -> StreamChunk:
        """Extract StreamChunk from parsed data."""
        # Try common fields
        content = (
            data.get("content")
            or data.get("delta", {}).get("content")
            or data.get("text")
            or data.get("response")
            or ""
        )

        finish = data.get("finish_reason") or data.get("stop_reason")
        done = data.get("done", False)

        return StreamChunk(
            delta=content,
            content=content,
            is_final=done or finish is not None,
            finish_reason=self._map_finish_reason(finish),
        )

    def _map_finish_reason(self, reason: str | None) -> FinishReason | None:
        """Map provider-specific finish reason to enum."""
        if not reason:
            return None

        reason = reason.lower()

        if reason in ("stop", "end_turn", "complete"):
            return FinishReason.STOP
        elif reason in ("length", "max_tokens"):
            return FinishReason.LENGTH
        elif reason in ("tool_calls", "tool_use", "function_call"):
            return FinishReason.TOOL_CALLS
        elif reason in ("content_filter", "safety"):
            return FinishReason.CONTENT_FILTER

        return FinishReason.STOP

    def reset(self) -> None:
        """Reset parser state."""
        self._buffer = ""
