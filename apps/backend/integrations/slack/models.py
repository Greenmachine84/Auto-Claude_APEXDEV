"""
APEX Development Platform - Slack Models
Phase 4: UI, Integrations & Analytics

Pydantic models for Slack API entities.
"""

from enum import Enum
from typing import Any

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
    app_token: str | None = Field(
        None, description="Slack app token for Socket Mode"
    )
    signing_secret: str | None = Field(
        None, description="Slack signing secret for webhooks"
    )
    default_channel: str | None = Field(
        None, description="Default channel for notifications"
    )


class SlackUser(BaseModel):
    """Slack user model."""

    id: str
    name: str
    real_name: str | None = None
    display_name: str | None = None
    email: str | None = None
    is_bot: bool = False
    is_admin: bool = False
    team_id: str | None = None
    tz: str | None = None
    profile: dict | None = None


class SlackChannel(BaseModel):
    """Slack channel model."""

    id: str
    name: str
    is_channel: bool = True
    is_private: bool = False
    is_archived: bool = False
    is_member: bool = False
    num_members: int | None = None
    topic: str | None = None
    purpose: str | None = None
    created: int | None = None
    creator: str | None = None


class SlackBlock(BaseModel):
    """Slack block element."""

    type: BlockType
    block_id: str | None = None
    text: dict | None = None
    accessory: dict | None = None
    elements: list[dict] | None = None
    fields: list[dict] | None = None

    @classmethod
    def section(
        cls,
        text: str,
        markdown: bool = True,
        accessory: dict | None = None,
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

    fallback: str | None = None
    color: str | None = None
    pretext: str | None = None
    author_name: str | None = None
    author_link: str | None = None
    author_icon: str | None = None
    title: str | None = None
    title_link: str | None = None
    text: str | None = None
    fields: list[dict] | None = None
    image_url: str | None = None
    thumb_url: str | None = None
    footer: str | None = None
    footer_icon: str | None = None
    ts: int | None = None


class SlackMessage(BaseModel):
    """Slack message model."""

    ts: str  # Message timestamp (ID)
    channel: str
    user: str | None = None
    text: str | None = None
    thread_ts: str | None = None
    blocks: list[SlackBlock] = Field(default_factory=list)
    attachments: list[SlackAttachment] = Field(default_factory=list)
    reactions: list[dict] = Field(default_factory=list)
    reply_count: int = 0
    reply_users_count: int = 0
    latest_reply: str | None = None
    subtype: str | None = None
    edited: dict | None = None


class MessageBuilder:
    """Builder for constructing Slack messages."""

    def __init__(self):
        self.text: str | None = None
        self.blocks: list[dict] = []
        self.attachments: list[dict] = []
        self.thread_ts: str | None = None
        self.reply_broadcast: bool = False
        self.unfurl_links: bool = True
        self.unfurl_media: bool = True

    def set_text(self, text: str) -> "MessageBuilder":
        """Set fallback text."""
        self.text = text
        return self

    def add_block(self, block: SlackBlock | dict) -> "MessageBuilder":
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
        color: str | None = None,
        title: str | None = None,
    ) -> "MessageBuilder":
        """Add attachment."""
        self.attachments.append(
            {
                "text": text,
                "color": color,
                "title": title,
            }
        )
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
