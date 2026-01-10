"""
APEX Development Platform - GitHub Integration
Phase 4: UI, Integrations & Analytics

GitHub API integration for repository, PR, and issue management.
"""

from .client import GitHubClient
from .models import (
    GitHubComment,
    GitHubConfig,
    GitHubIssue,
    GitHubLabel,
    GitHubMilestone,
    GitHubPullRequest,
    GitHubRepository,
    GitHubReview,
    GitHubUser,
    IssueState,
    PullRequestState,
    ReviewState,
)
from .service import GitHubService
from .webhooks import GitHubWebhookHandler, WebhookEvent

__all__ = [
    # Client
    "GitHubClient",
    # Models
    "GitHubConfig",
    "GitHubRepository",
    "GitHubPullRequest",
    "GitHubIssue",
    "GitHubReview",
    "GitHubComment",
    "GitHubUser",
    "GitHubLabel",
    "GitHubMilestone",
    "PullRequestState",
    "IssueState",
    "ReviewState",
    # Service
    "GitHubService",
    # Webhooks
    "GitHubWebhookHandler",
    "WebhookEvent",
]
