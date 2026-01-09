"""
APEX Development Platform - JIRA Webhooks
Phase 4: UI, Integrations & Analytics

Webhook handler for JIRA events.
"""

import hashlib
import hmac
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """JIRA webhook events."""

    ISSUE_CREATED = "jira:issue_created"
    ISSUE_UPDATED = "jira:issue_updated"
    ISSUE_DELETED = "jira:issue_deleted"
    COMMENT_CREATED = "comment_created"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    SPRINT_CREATED = "sprint_created"
    SPRINT_UPDATED = "sprint_updated"
    SPRINT_STARTED = "sprint_started"
    SPRINT_CLOSED = "sprint_closed"


@dataclass
class WebhookPayload:
    """Webhook payload data."""

    event: WebhookEvent
    timestamp: int
    user: dict
    issue: dict | None
    changelog: dict | None
    comment: dict | None
    data: dict


EventHandler = Callable[[WebhookPayload], Coroutine[Any, Any, None]]


@dataclass
class JiraWebhookHandler:
    """JIRA webhook handler."""

    secret: str | None = None
    handlers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not self.secret:
            return True

        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def register(
        self,
        event: WebhookEvent,
    ) -> Callable[[EventHandler], EventHandler]:
        """Register event handler decorator."""
        key = event.value

        def decorator(handler: EventHandler) -> EventHandler:
            if key not in self.handlers:
                self.handlers[key] = []
            self.handlers[key].append(handler)
            return handler

        return decorator

    def on_issue_created(self) -> Callable[[EventHandler], EventHandler]:
        """Register issue created handler."""
        return self.register(WebhookEvent.ISSUE_CREATED)

    def on_issue_updated(self) -> Callable[[EventHandler], EventHandler]:
        """Register issue updated handler."""
        return self.register(WebhookEvent.ISSUE_UPDATED)

    def on_comment_created(self) -> Callable[[EventHandler], EventHandler]:
        """Register comment created handler."""
        return self.register(WebhookEvent.COMMENT_CREATED)

    def on_sprint_started(self) -> Callable[[EventHandler], EventHandler]:
        """Register sprint started handler."""
        return self.register(WebhookEvent.SPRINT_STARTED)

    async def handle(
        self,
        payload: dict,
        signature: str | None = None,
        raw_payload: bytes | None = None,
    ) -> bool:
        """Handle incoming webhook."""
        # Verify signature if provided
        if raw_payload and signature:
            if not self.verify_signature(raw_payload, signature):
                logger.warning("Invalid webhook signature")
                return False

        webhook_event = payload.get("webhookEvent")
        if not webhook_event:
            logger.debug("Missing webhookEvent in payload")
            return True

        try:
            event = WebhookEvent(webhook_event)
        except ValueError:
            logger.debug(f"Unhandled JIRA webhook event: {webhook_event}")
            return True

        webhook_payload = WebhookPayload(
            event=event,
            timestamp=payload.get("timestamp", 0),
            user=payload.get("user", {}),
            issue=payload.get("issue"),
            changelog=payload.get("changelog"),
            comment=payload.get("comment"),
            data=payload,
        )

        handlers = self.handlers.get(event.value, [])
        if not handlers:
            logger.debug(f"No handlers for {event.value}")
            return True

        for handler in handlers:
            try:
                await handler(webhook_payload)
            except Exception as e:
                logger.exception(f"Webhook handler error: {e}")

        return True
