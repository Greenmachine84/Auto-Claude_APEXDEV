"""
APEX Development Platform - Linear Webhooks
Phase 4: UI, Integrations & Analytics

Webhook handler for Linear events.
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
    """Linear webhook events."""

    ISSUE_CREATE = "Issue.create"
    ISSUE_UPDATE = "Issue.update"
    ISSUE_REMOVE = "Issue.remove"
    COMMENT_CREATE = "Comment.create"
    COMMENT_UPDATE = "Comment.update"
    COMMENT_REMOVE = "Comment.remove"
    PROJECT_CREATE = "Project.create"
    PROJECT_UPDATE = "Project.update"
    CYCLE_CREATE = "Cycle.create"
    CYCLE_UPDATE = "Cycle.update"


@dataclass
class WebhookPayload:
    """Webhook payload data."""

    type: str  # e.g., "Issue"
    action: str  # e.g., "create"
    event: WebhookEvent
    data: dict
    created_at: str
    url: str | None = None
    organization_id: str | None = None
    webhook_id: str | None = None


EventHandler = Callable[[WebhookPayload], Coroutine[Any, Any, None]]


@dataclass
class LinearWebhookHandler:
    """Linear webhook handler."""

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

    def on_issue_create(self) -> Callable[[EventHandler], EventHandler]:
        """Register issue create handler."""
        return self.register(WebhookEvent.ISSUE_CREATE)

    def on_issue_update(self) -> Callable[[EventHandler], EventHandler]:
        """Register issue update handler."""
        return self.register(WebhookEvent.ISSUE_UPDATE)

    def on_comment_create(self) -> Callable[[EventHandler], EventHandler]:
        """Register comment create handler."""
        return self.register(WebhookEvent.COMMENT_CREATE)

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

        event_type = payload.get("type")  # e.g., "Issue"
        action = payload.get("action")  # e.g., "create"

        if not event_type or not action:
            logger.debug("Missing type or action in webhook payload")
            return True

        event_key = f"{event_type}.{action}"
        try:
            event = WebhookEvent(event_key)
        except ValueError:
            logger.debug(f"Unhandled webhook event: {event_key}")
            return True

        webhook_payload = WebhookPayload(
            type=event_type,
            action=action,
            event=event,
            data=payload.get("data", {}),
            created_at=payload.get("createdAt", ""),
            url=payload.get("url"),
            organization_id=payload.get("organizationId"),
            webhook_id=payload.get("webhookId"),
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
