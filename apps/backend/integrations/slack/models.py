"""
APEX Development Platform - Slack Models
Phase 4: UI, Integrations & Analytics

Pydantic models for Slack API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    """Slack block types."""

    SECTION = "section"
    DIVIDER = "divider"
    IMAGE = "image"
    ACTIONS = "actions"
    CONTEXT = "context"
    HEADER = "header"
    INPUT = "input"
    FILE = "file"
    RICH_TEXT = "rich_text"


class SlackConfig(BaseModel):
    """Slack integration configuration."""

    bot_token: str = Field(..., description="Slack bot OAuth token (xoxb-...)")
    app_token: Optional[str] = Field(None, description="Slack app token for Socket Mode")
    signing_secret: Optional[str] = Field(None, description="Slack signing secret for webhooks")
    default_channel: Optional[str] = Field(None, description="Default channel for notifications")


class SlackUser(BaseModel):
    """Slack user model."""

    id: str
    name: str
    real_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_bot: bool = False
    is_admin: bool = False
    team_id: Optional[str] = None
    tz: Optional[str] = None
    profile: Optional[dict] = None


class SlackChannel(BaseModel):
    """Slack channel model."""

    id: str
    name: str
    is_channel: bool = True
    is_private: bool = False
    is_archived: bool = False
    is_member: bool = False
    num_members: Optional[int] = None
    topic: Optional[str] = None
    purpose: Optional[str] = None
    created: Optional[int] = None
    creator: Optional[str] = None


class SlackBlock(BaseModel):
    """Slack block element."""

    type: BlockType
    block_id: Optional[str] = None
    text: Optional[dict] = None
    accessory: Optional[dict] = None
    elements: Optional[list[dict]] = None
    fields: Optional[list[dict]] = None

    @classmethod
    def section(
        cls,
        text: str,
        markdown: bool = True,
        accessory: Optional[dict] = None,
    ) -> "SlackBlock":
        """Create section block."""
        return cls(
            type=BlockType.SECTION,
            text={"type": "mrkdwn" if markdown else "plain_text", "text": text},
            accessory=accessory,
        )

    @classmethod
    def divider(cls) -> "SlackBlock":
        """Create divider block."""
        return cls(type=BlockType.DIVIDER)

    @classmethod
    def header(cls, text: str) -> "SlackBlock":
        """Create header block."""
        return cls(
            type=BlockType.HEADER,
            text={"type": "plain_text", "text": text},
        )

    @classmethod
    def context(cls, elements: list[str]) -> "SlackBlock":
        """Create context block."""
        return cls(
            type=BlockType.CONTEXT,
            elements=[{"type": "mrkdwn", "text": e} for e in elements],
        )


class SlackAttachment(BaseModel):
    """Slack message attachment (legacy format)."""

    fallback: Optional[str] = None
    color: Optional[str] = None
    pretext: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
    author_icon: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    fields: Optional[list[dict]] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None


class SlackMessage(BaseModel):
    """Slack message model."""

    ts: str  # Message timestamp (ID)
    channel: str
    user: Optional[str] = None
    text: Optional[str] = None
    thread_ts: Optional[str] = None
    blocks: list[SlackBlock] = Field(default_factory=list)
    attachments: list[SlackAttachment] = Field(default_factory=list)
    reactions: list[dict] = Field(default_factory=list)
    reply_count: int = 0
    reply_users_count: int = 0
    latest_reply: Optional[str] = None
    subtype: Optional[str] = None
    edited: Optional[dict] = None


class MessageBuilder:
    """Builder for constructing Slack messages."""

    def __init__(self):
        self.text: Optional[str] = None
        self.blocks: list[dict] = []
        self.attachments: list[dict] = []
        self.thread_ts: Optional[str] = None
        self.reply_broadcast: bool = False
        self.unfurl_links: bool = True
        self.unfurl_media: bool = True

    def set_text(self, text: str) -> "MessageBuilder":
        """Set fallback text."""
        self.text = text
        return self

    def add_block(self, block: Union[SlackBlock, dict]) -> "MessageBuilder":
        """Add a block."""
        if isinstance(block, SlackBlock):
            self.blocks.append(block.model_dump(exclude_none=True))
        else:
            self.blocks.append(block)
        return self

    def add_section(self, text: str, markdown: bool = True) -> "MessageBuilder":
        """Add section block."""
        return self.add_block(SlackBlock.section(text, markdown))

    def add_divider(self) -> "MessageBuilder":
        """Add divider block."""
        return self.add_block(SlackBlock.divider())

    def add_header(self, text: str) -> "MessageBuilder":
        """Add header block."""
        return self.add_block(SlackBlock.header(text))

    def add_context(self, elements: list[str]) -> "MessageBuilder":
        """Add context block."""
        return self.add_block(SlackBlock.context(elements))

    def add_attachment(
        self,
        text: str,
        color: Optional[str] = None,
        title: Optional[str] = None,
    ) -> "MessageBuilder":
        """Add attachment."""
        self.attachments.append({
            "text": text,
            "color": color,
            "title": title,
        })
        return self

    def in_thread(self, thread_ts: str, broadcast: bool = False) -> "MessageBuilder":
        """Reply in thread."""
        self.thread_ts = thread_ts
        self.reply_broadcast = broadcast
        return self

    def build(self) -> dict[str, Any]:
        """Build message payload."""
        payload: dict[str, Any] = {}
        if self.text:
            payload["text"] = self.text
        if self.blocks:
            payload["blocks"] = self.blocks
        if self.attachments:
            payload["attachments"] = self.attachments
        if self.thread_ts:
            payload["thread_ts"] = self.thread_ts
            if self.reply_broadcast:
                payload["reply_broadcast"] = True
        payload["unfurl_links"] = self.unfurl_links
        payload["unfurl_media"] = self.unfurl_media
        return payload
