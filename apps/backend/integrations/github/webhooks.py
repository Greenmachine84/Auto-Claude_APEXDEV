"""
APEX Development Platform - GitHub Webhooks
Phase 4: UI, Integrations & Analytics

Webhook handler for GitHub events.
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """GitHub webhook events."""

    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    CREATE = "create"
    DELETE = "delete"
    FORK = "fork"
    RELEASE = "release"
    WORKFLOW_RUN = "workflow_run"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"


@dataclass
class WebhookPayload:
    """Webhook payload data."""

    event: WebhookEvent
    action: Optional[str]
    sender: dict
    repository: dict
    data: dict


EventHandler = Callable[[WebhookPayload], Coroutine[Any, Any, None]]


@dataclass
class GitHubWebhookHandler:
    """GitHub webhook handler."""

    secret: Optional[str] = None
    handlers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not self.secret:
            return True

        if not signature or not signature.startswith("sha256="):
            return False

        expected = "sha256=" + hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

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

    def on_pull_request(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register pull request handler."""
        return self.register(WebhookEvent.PULL_REQUEST, action)

    def on_pull_request_review(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register pull request review handler."""
        return self.register(WebhookEvent.PULL_REQUEST_REVIEW, action)

    def on_issue(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register issue handler."""
        return self.register(WebhookEvent.ISSUES, action)

    def on_issue_comment(self, action: Optional[str] = None) -> Callable[[EventHandler], EventHandler]:
        """Register issue comment handler."""
        return self.register(WebhookEvent.ISSUE_COMMENT, action)

    def on_push(self) -> Callable[[EventHandler], EventHandler]:
        """Register push handler."""
        return self.register(WebhookEvent.PUSH)

    async def handle(
        self,
        event_type: str,
        payload: dict,
        signature: Optional[str] = None,
        raw_payload: Optional[bytes] = None,
    ) -> bool:
        """Handle incoming webhook."""
        # Verify signature if provided
        if raw_payload and signature:
            if not self.verify_signature(raw_payload, signature):
                logger.warning("Invalid webhook signature")
                return False

        try:
            event = WebhookEvent(event_type)
        except ValueError:
            logger.debug(f"Unhandled webhook event: {event_type}")
            return True

        action = payload.get("action")
        webhook_payload = WebhookPayload(
            event=event,
            action=action,
            sender=payload.get("sender", {}),
            repository=payload.get("repository", {}),
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
