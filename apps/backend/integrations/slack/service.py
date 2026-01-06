"""
APEX Development Platform - Slack Service
Phase 4: UI, Integrations & Analytics

High-level service for Slack operations.
"""

import logging
from typing import Optional, Union

from .client import SlackClient
from .models import (
    SlackConfig,
    SlackChannel,
    SlackMessage,
    SlackUser,
    SlackBlock,
    MessageBuilder,
)

logger = logging.getLogger(__name__)


class SlackService:
    """High-level Slack service."""

    def __init__(self, config: SlackConfig):
        self.config = config
        self.client = SlackClient(config)
        self._default_channel = config.default_channel

    async def close(self) -> None:
        """Close service."""
        await self.client.close()

    async def test_connection(self) -> dict:
        """Test Slack connection."""
        return await self.client.auth_test()

    # Channel methods
    async def list_channels(
        self,
        include_private: bool = False,
        exclude_archived: bool = True,
    ) -> list[SlackChannel]:
        """List channels."""
        types = "public_channel"
        if include_private:
            types = "public_channel,private_channel"

        result = await self.client.conversations_list(
            types=types,
            exclude_archived=exclude_archived,
        )
        return [SlackChannel(**c) for c in result.get("channels", [])]

    async def get_channel(self, channel_id: str) -> SlackChannel:
        """Get channel by ID."""
        result = await self.client.conversations_info(channel_id)
        return SlackChannel(**result["channel"])

    # User methods
    async def list_users(self) -> list[SlackUser]:
        """List users."""
        result = await self.client.users_list()
        return [
            SlackUser(
                id=m["id"],
                name=m.get("name", ""),
                real_name=m.get("real_name"),
                display_name=m.get("profile", {}).get("display_name"),
                email=m.get("profile", {}).get("email"),
                is_bot=m.get("is_bot", False),
                is_admin=m.get("is_admin", False),
                team_id=m.get("team_id"),
                tz=m.get("tz"),
                profile=m.get("profile"),
            )
            for m in result.get("members", [])
        ]

    async def get_user(self, user_id: str) -> SlackUser:
        """Get user by ID."""
        result = await self.client.users_info(user_id)
        m = result["user"]
        return SlackUser(
            id=m["id"],
            name=m.get("name", ""),
            real_name=m.get("real_name"),
            display_name=m.get("profile", {}).get("display_name"),
            email=m.get("profile", {}).get("email"),
            is_bot=m.get("is_bot", False),
            is_admin=m.get("is_admin", False),
            team_id=m.get("team_id"),
            tz=m.get("tz"),
            profile=m.get("profile"),
        )

    # Message methods
    async def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        blocks: Optional[list[Union[SlackBlock, dict]]] = None,
        thread_ts: Optional[str] = None,
    ) -> SlackMessage:
        """Send a message."""
        target = channel or self._default_channel
        if not target:
            raise ValueError("Channel must be specified")

        block_dicts = None
        if blocks:
            block_dicts = [
                b.model_dump(exclude_none=True) if isinstance(b, SlackBlock) else b
                for b in blocks
            ]

        result = await self.client.chat_post_message(
            channel=target,
            text=text,
            blocks=block_dicts,
            thread_ts=thread_ts,
        )
        return SlackMessage(
            ts=result["ts"],
            channel=result["channel"],
            text=text,
            thread_ts=thread_ts,
        )

    async def send_rich_message(
        self,
        builder: MessageBuilder,
        channel: Optional[str] = None,
    ) -> SlackMessage:
        """Send a rich message using builder."""
        target = channel or self._default_channel
        if not target:
            raise ValueError("Channel must be specified")

        payload = builder.build()
        result = await self.client.chat_post_message(
            channel=target,
            **payload,
        )
        return SlackMessage(
            ts=result["ts"],
            channel=result["channel"],
            text=payload.get("text"),
            thread_ts=payload.get("thread_ts"),
        )

    async def update_message(
        self,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[list[Union[SlackBlock, dict]]] = None,
    ) -> SlackMessage:
        """Update a message."""
        block_dicts = None
        if blocks:
            block_dicts = [
                b.model_dump(exclude_none=True) if isinstance(b, SlackBlock) else b
                for b in blocks
            ]

        result = await self.client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
            blocks=block_dicts,
        )
        return SlackMessage(
            ts=result["ts"],
            channel=result["channel"],
            text=text,
        )

    async def delete_message(self, channel: str, ts: str) -> None:
        """Delete a message."""
        await self.client.chat_delete(channel, ts)

    async def add_reaction(self, channel: str, ts: str, emoji: str) -> None:
        """Add reaction to message."""
        await self.client.reactions_add(channel, ts, emoji)

    async def remove_reaction(self, channel: str, ts: str, emoji: str) -> None:
        """Remove reaction from message."""
        await self.client.reactions_remove(channel, ts, emoji)

    # Notification helpers
    async def notify_task_completed(
        self,
        task_title: str,
        task_id: str,
        agent_name: str,
        channel: Optional[str] = None,
    ) -> SlackMessage:
        """Send task completion notification."""
        builder = MessageBuilder()
        builder.set_text(f"✅ Task completed: {task_title}")
        builder.add_header("Task Completed")
        builder.add_section(f"*{task_title}*")
        builder.add_context([f"Task ID: {task_id}", f"Completed by: {agent_name}"])

        return await self.send_rich_message(builder, channel)

    async def notify_error(
        self,
        error_message: str,
        context: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> SlackMessage:
        """Send error notification."""
        builder = MessageBuilder()
        builder.set_text(f"❌ Error: {error_message}")
        builder.add_section(f":x: *Error*\n{error_message}")
        if context:
            builder.add_context([context])

        return await self.send_rich_message(builder, channel)

    async def notify_pr_ready(
        self,
        pr_title: str,
        pr_url: str,
        repo_name: str,
        channel: Optional[str] = None,
    ) -> SlackMessage:
        """Send PR ready for review notification."""
        builder = MessageBuilder()
        builder.set_text(f"🔍 PR ready for review: {pr_title}")
        builder.add_header("Pull Request Ready")
        builder.add_section(f"*<{pr_url}|{pr_title}>*")
        builder.add_context([f"Repository: {repo_name}"])

        return await self.send_rich_message(builder, channel)
