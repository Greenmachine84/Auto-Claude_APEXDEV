"""
APEX Development Platform - Slack Client
Phase 4: UI, Integrations & Analytics

HTTP client for Slack API interactions.
"""

import logging
from typing import Any, Optional

import httpx

from .models import SlackConfig

logger = logging.getLogger(__name__)


class SlackClientError(Exception):
    """Slack client error."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code


class SlackClient:
    """Slack Web API HTTP client."""

    BASE_URL = "https://slack.com/api"

    def __init__(self, config: SlackConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.config.bot_token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _call(
        self,
        method: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Call Slack API method."""
        client = await self._get_client()
        try:
            response = await client.post(
                f"/{method}",
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("ok"):
                error = result.get("error", "unknown_error")
                logger.error(f"Slack API error: {error}")
                raise SlackClientError(error, error)

            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"Slack API HTTP error: {e}")
            raise SlackClientError(str(e)) from e
        except httpx.RequestError as e:
            logger.error(f"Slack API request failed: {e}")
            raise SlackClientError(str(e)) from e

    # Auth
    async def auth_test(self) -> dict[str, Any]:
        """Test authentication."""
        return await self._call("auth.test")

    # Chat
    async def chat_post_message(
        self,
        channel: str,
        text: Optional[str] = None,
        blocks: Optional[list[dict]] = None,
        attachments: Optional[list[dict]] = None,
        thread_ts: Optional[str] = None,
        reply_broadcast: bool = False,
    ) -> dict[str, Any]:
        """Post message to channel."""
        payload = {"channel": channel}
        if text:
            payload["text"] = text
        if blocks:
            payload["blocks"] = blocks
        if attachments:
            payload["attachments"] = attachments
        if thread_ts:
            payload["thread_ts"] = thread_ts
            if reply_broadcast:
                payload["reply_broadcast"] = True
        return await self._call("chat.postMessage", json_data=payload)

    async def chat_update(
        self,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Update message."""
        payload = {"channel": channel, "ts": ts}
        if text:
            payload["text"] = text
        if blocks:
            payload["blocks"] = blocks
        return await self._call("chat.update", json_data=payload)

    async def chat_delete(self, channel: str, ts: str) -> dict[str, Any]:
        """Delete message."""
        return await self._call("chat.delete", json_data={"channel": channel, "ts": ts})

    # Conversations
    async def conversations_list(
        self,
        types: str = "public_channel,private_channel",
        exclude_archived: bool = True,
        limit: int = 100,
    ) -> dict[str, Any]:
        """List conversations."""
        return await self._call(
            "conversations.list",
            json_data={
                "types": types,
                "exclude_archived": exclude_archived,
                "limit": limit,
            },
        )

    async def conversations_info(self, channel: str) -> dict[str, Any]:
        """Get conversation info."""
        return await self._call("conversations.info", json_data={"channel": channel})

    async def conversations_history(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get conversation history."""
        payload = {"channel": channel, "limit": limit}
        if oldest:
            payload["oldest"] = oldest
        if latest:
            payload["latest"] = latest
        return await self._call("conversations.history", json_data=payload)

    async def conversations_replies(
        self,
        channel: str,
        ts: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get thread replies."""
        return await self._call(
            "conversations.replies",
            json_data={"channel": channel, "ts": ts, "limit": limit},
        )

    # Users
    async def users_list(self, limit: int = 100) -> dict[str, Any]:
        """List users."""
        return await self._call("users.list", json_data={"limit": limit})

    async def users_info(self, user: str) -> dict[str, Any]:
        """Get user info."""
        return await self._call("users.info", json_data={"user": user})

    # Reactions
    async def reactions_add(self, channel: str, timestamp: str, name: str) -> dict[str, Any]:
        """Add reaction."""
        return await self._call(
            "reactions.add",
            json_data={"channel": channel, "timestamp": timestamp, "name": name},
        )

    async def reactions_remove(self, channel: str, timestamp: str, name: str) -> dict[str, Any]:
        """Remove reaction."""
        return await self._call(
            "reactions.remove",
            json_data={"channel": channel, "timestamp": timestamp, "name": name},
        )
