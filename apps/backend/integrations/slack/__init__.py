"""
APEX Development Platform - Slack Integration
Phase 4: UI, Integrations & Analytics

Slack API integration for messaging and notifications.
"""

from .client import SlackClient
from .models import (
    SlackConfig,
    SlackMessage,
    SlackChannel,
    SlackUser,
    SlackAttachment,
    SlackBlock,
    BlockType,
)
from .service import SlackService
from .webhooks import SlackWebhookHandler, EventType

__all__ = [
    # Client
    "SlackClient",
    # Models
    "SlackConfig",
    "SlackMessage",
    "SlackChannel",
    "SlackUser",
    "SlackAttachment",
    "SlackBlock",
    "BlockType",
    # Service
    "SlackService",
    # Webhooks
    "SlackWebhookHandler",
    "EventType",
]
