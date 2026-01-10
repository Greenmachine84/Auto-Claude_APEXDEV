"""Message format types for LLM communication.

Part of Phase 2: LLM Architecture
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union


class MessageRole(Enum):
    """Message roles in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"  # Legacy OpenAI


class ContentType(Enum):
    """Types of message content."""

    TEXT = "text"
    IMAGE = "image"
    IMAGE_URL = "image_url"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


@dataclass
class ImageContent:
    """Image content for multimodal messages."""

    url: str
    media_type: str = "image/png"
    detail: str = "auto"  # auto, low, high

    def to_openai_format(self) -> dict[str, Any]:
        return {
            "type": "image_url",
            "image_url": {"url": self.url, "detail": self.detail},
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        return {
            "type": "image",
            "source": {
                "type": "url" if self.url.startswith("http") else "base64",
                "media_type": self.media_type,
                "data": self.url,
            },
        }


@dataclass
class TextContent:
    """Text content block."""

    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "text", "text": self.text}


@dataclass
class ToolUseContent:
    """Tool use request content."""

    id: str
    name: str
    input: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "tool_use",
            "id": self.id,
            "name": self.name,
            "input": self.input,
        }


@dataclass
class ToolResultContent:
    """Tool result content."""

    tool_use_id: str
    content: str
    is_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = {
            "type": "tool_result",
            "tool_use_id": self.tool_use_id,
            "content": self.content,
        }
        if self.is_error:
            result["is_error"] = True
        return result


ContentBlock = Union[TextContent, ImageContent, ToolUseContent, ToolResultContent]


@dataclass
class ToolCall:
    """A tool call from the assistant."""

    id: str
    name: str
    arguments: str | dict[str, Any]

    def to_openai_format(self) -> dict[str, Any]:
        args = (
            self.arguments
            if isinstance(self.arguments, str)
            else __import__("json").dumps(self.arguments)
        )
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": args},
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        return {
            "type": "tool_use",
            "id": self.id,
            "name": self.name,
            "input": self.arguments
            if isinstance(self.arguments, dict)
            else __import__("json").loads(self.arguments),
        }


@dataclass
class Message:
    """A message in a conversation."""

    role: str  # system, user, assistant, tool
    content: str | list[ContentBlock]
    name: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None  # For tool result messages
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI message format."""
        msg: dict[str, Any] = {"role": self.role}

        if isinstance(self.content, str):
            msg["content"] = self.content
        elif isinstance(self.content, list):
            msg["content"] = []
            for block in self.content:
                if isinstance(block, TextContent):
                    msg["content"].append({"type": "text", "text": block.text})
                elif isinstance(block, ImageContent):
                    msg["content"].append(block.to_openai_format())

        if self.name:
            msg["name"] = self.name

        if self.tool_calls:
            msg["tool_calls"] = [tc.to_openai_format() for tc in self.tool_calls]

        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id

        return msg

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic message format."""
        msg: dict[str, Any] = {"role": self.role}

        if isinstance(self.content, str):
            msg["content"] = self.content
        elif isinstance(self.content, list):
            msg["content"] = []
            for block in self.content:
                if hasattr(block, "to_dict"):
                    msg["content"].append(block.to_dict())
                elif hasattr(block, "to_anthropic_format"):
                    msg["content"].append(block.to_anthropic_format())

        return msg

    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message."""
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str | list[ContentBlock]) -> "Message":
        """Create a user message."""
        return cls(role="user", content=content)

    @classmethod
    def assistant(
        cls, content: str, tool_calls: list[ToolCall] | None = None
    ) -> "Message":
        """Create an assistant message."""
        return cls(role="assistant", content=content, tool_calls=tool_calls)

    @classmethod
    def tool_result(
        cls, tool_call_id: str, content: str, is_error: bool = False
    ) -> "Message":
        """Create a tool result message."""
        return cls(
            role="tool",
            content=content,
            tool_call_id=tool_call_id,
            metadata={"is_error": is_error} if is_error else {},
        )


@dataclass
class Conversation:
    """A conversation consisting of messages."""

    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)

    def add_system(self, content: str) -> None:
        """Add a system message."""
        self.add(Message.system(content))

    def add_user(self, content: str | list[ContentBlock]) -> None:
        """Add a user message."""
        self.add(Message.user(content))

    def add_assistant(
        self, content: str, tool_calls: list[ToolCall] | None = None
    ) -> None:
        """Add an assistant message."""
        self.add(Message.assistant(content, tool_calls))

    def add_tool_result(
        self, tool_call_id: str, content: str, is_error: bool = False
    ) -> None:
        """Add a tool result."""
        self.add(Message.tool_result(tool_call_id, content, is_error))

    def to_openai_format(self) -> list[dict[str, Any]]:
        """Convert to OpenAI messages format."""
        return [m.to_openai_format() for m in self.messages]

    def to_anthropic_format(self) -> tuple[str | None, list[dict[str, Any]]]:
        """Convert to Anthropic format (system, messages)."""
        system = None
        messages = []

        for m in self.messages:
            if m.role == "system":
                system = m.content if isinstance(m.content, str) else str(m.content)
            else:
                messages.append(m.to_anthropic_format())

        return system, messages

    @property
    def last_message(self) -> Message | None:
        """Get the last message."""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: str) -> list[Message]:
        """Get all messages with a specific role."""
        return [m for m in self.messages if m.role == role]
