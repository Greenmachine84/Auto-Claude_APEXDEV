"""
APEX Development Platform - Slack Webhooks
Phase 4: UI, Integrations & Analytics

Webhook and event handler for Slack events.
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Slack event types."""

    MESSAGE = "message"
    APP_MENTION = "app_mention"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    CHANNEL_CREATED = "channel_created"
    MEMBER_JOINED_CHANNEL = "member_joined_channel"
    MEMBER_LEFT_CHANNEL = "member_left_channel"
    APP_HOME_OPENED = "app_home_opened"


@dataclass
class EventPayload:
    """Event payload data."""

    type: EventType
    event_ts: str
    user: Optional[str]
    channel: Optional[str]
    data: dict
    team_id: Optional[str] = None
    api_app_id: Optional[str] = None


EventHandler = Callable[[EventPayload], Coroutine[Any, Any, None]]


@dataclass
class SlackWebhookHandler:
    """Slack event and webhook handler."""

    signing_secret: Optional[str] = None
    handlers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def verify_signature(
        self,
        body: bytes,
        timestamp: str,
        signature: str,
    ) -> bool:
        """Verify Slack request signature."""
        if not self.signing_secret:
            return True

        # Check timestamp freshness (within 5 minutes)
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > 300:
                logger.warning("Slack request timestamp too old")
                return False
        except ValueError:
            return False

        # Compute signature
        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        computed = "v0=" + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, signature)

    def register(self, event_type: EventType) -> Callable[[EventHandler], EventHandler]:
        """Register event handler decorator."""
        key = event_type.value

        def decorator(handler: EventHandler) -> EventHandler:
            if key not in self.handlers:
                self.handlers[key] = []
            self.handlers[key].append(handler)
            return handler

        return decorator

    def on_message(self) -> Callable[[EventHandler], EventHandler]:
        """Register message handler."""
        return self.register(EventType.MESSAGE)

    def on_app_mention(self) -> Callable[[EventHandler], EventHandler]:
        """Register app mention handler."""
        return self.register(EventType.APP_MENTION)

    def on_reaction_added(self) -> Callable[[EventHandler], EventHandler]:
        """Register reaction added handler."""
        return self.register(EventType.REACTION_ADDED)

    async def handle(
        self,
        payload: dict,
        body: Optional[bytes] = None,
        timestamp: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> Optional[dict]:
        """Handle incoming Slack event."""
        # Handle URL verification challenge
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}

        # Verify signature if provided
        if body and timestamp and signature:
            if not self.verify_signature(body, timestamp, signature):
                logger.warning("Invalid Slack signature")
                return None

        # Handle event callback
        if payload.get("type") != "event_callback":
            return None

        event = payload.get("event", {})
        event_type = event.get("type")

        if not event_type:
            return None

        try:
            evt = EventType(event_type)
        except ValueError:
            logger.debug(f"Unhandled Slack event: {event_type}")
            return None

        # Skip bot messages to prevent loops
        if event.get("bot_id"):
            return None

        event_payload = EventPayload(
            type=evt,
            event_ts=event.get("event_ts", ""),
            user=event.get("user"),
            channel=event.get("channel"),
            data=event,
            team_id=payload.get("team_id"),
            api_app_id=payload.get("api_app_id"),
        )

        handlers = self.handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_payload)
            except Exception as e:
                logger.exception(f"Slack event handler error: {e}")

        return None
