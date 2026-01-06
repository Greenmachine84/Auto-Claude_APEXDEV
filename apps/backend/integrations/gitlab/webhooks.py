"""
APEX Development Platform - GitLab Webhooks
Phase 4: UI, Integrations & Analytics

Webhook handler for GitLab events.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """GitLab webhook events."""

    PUSH = "push"
    TAG_PUSH = "tag_push"
    MERGE_REQUEST = "merge_request"
    ISSUE = "issue"
    NOTE = "note"
    PIPELINE = "pipeline"
    JOB = "job"
    DEPLOYMENT = "deployment"
    WIKI_PAGE = "wiki_page"
    RELEASE = "release"


@dataclass
class WebhookPayload:
    """Webhook payload data."""

    event: WebhookEvent
    object_kind: str
    event_name: Optional[str]
    user: dict
    project: dict
    data: dict


EventHandler = Callable[[WebhookPayload], Coroutine[Any, Any, None]]


@dataclass
class GitLabWebhookHandler:
    """GitLab webhook handler."""

    secret: Optional[str] = None
    handlers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def verify_token(self, token: Optional[str]) -> bool:
        """Verify webhook secret token."""
        if not self.secret:
            return True
        return token == self.secret

    def register(
        self,
        event: WebhookEvent,
        action: Optional[str] = None,
    ) -> Callable[[EventHandler], EventHandler]:
        """Register event handler decorator."""
        key = f"{event.value}:{action}" if action else event.value

        def decorator(handler: EventHandler) -> EventHandler:
            if key not in self.handlers:
                self.handlers[key] = []
            self.handlers[key].append(handler)
            return handler

        return decorator

    def on_merge_request(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register merge request handler."""
        return self.register(WebhookEvent.MERGE_REQUEST, action)

    def on_issue(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register issue handler."""
        return self.register(WebhookEvent.ISSUE, action)

    def on_note(self) -> Callable[[EventHandler], EventHandler]:
        """Register note handler."""
        return self.register(WebhookEvent.NOTE)

    def on_push(self) -> Callable[[EventHandler], EventHandler]:
        """Register push handler."""
        return self.register(WebhookEvent.PUSH)

    def on_pipeline(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register pipeline handler."""
        return self.register(WebhookEvent.PIPELINE, action)

    async def handle(
        self,
        payload: dict,
        token: Optional[str] = None,
    ) -> bool:
        """Handle incoming webhook."""
        # Verify token
        if not self.verify_token(token):
            logger.warning("Invalid webhook token")
            return False

        object_kind = payload.get("object_kind")
        if not object_kind:
            logger.debug("Missing object_kind in webhook payload")
            return True

        try:
            event = WebhookEvent(object_kind)
        except ValueError:
            logger.debug(f"Unhandled webhook event: {object_kind}")
            return True

        # Extract action from object_attributes if present
        action = None
        object_attributes = payload.get("object_attributes", {})
        if isinstance(object_attributes, dict):
            action = object_attributes.get("action")

        webhook_payload = WebhookPayload(
            event=event,
            object_kind=object_kind,
            event_name=payload.get("event_name"),
            user=payload.get("user", {}),
            project=payload.get("project", {}),
            data=payload,
        )

        # Get handlers for this event
        keys = [event.value]
        if action:
            keys.append(f"{event.value}:{action}")

        handlers: list[EventHandler] = []
        for key in keys:
            handlers.extend(self.handlers.get(key, []))

        if not handlers:
            logger.debug(f"No handlers for {event.value}:{action}")
            return True

        # Execute handlers
        for handler in handlers:
            try:
                await handler(webhook_payload)
            except Exception as e:
                logger.exception(f"Webhook handler error: {e}")

        return True
