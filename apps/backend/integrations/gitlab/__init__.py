"""
APEX Development Platform - GitLab Integration
Phase 4: UI, Integrations & Analytics

GitLab API integration for project, MR, and issue management.
"""

from .client import GitLabClient
from .models import (
    GitLabConfig,
    GitLabIssue,
    GitLabLabel,
    GitLabMergeRequest,
    GitLabMilestone,
    GitLabNote,
    GitLabProject,
    GitLabUser,
    IssueState,
    MergeRequestState,
)
from .service import GitLabService
from .webhooks import GitLabWebhookHandler, WebhookEvent

__all__ = [
    # Client
    "GitLabClient",
    # Models
    "GitLabConfig",
    "GitLabProject",
    "GitLabMergeRequest",
    "GitLabIssue",
    "GitLabNote",
    "GitLabUser",
    "GitLabLabel",
    "GitLabMilestone",
    "MergeRequestState",
    "IssueState",
    # Service
    "GitLabService",
    # Webhooks
    "GitLabWebhookHandler",
    "WebhookEvent",
]
