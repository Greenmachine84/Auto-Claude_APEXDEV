"""
APEX Development Platform - GitHub Models
Phase 4: UI, Integrations & Analytics

Pydantic models for GitHub API entities.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class PullRequestState(str, Enum):
    """Pull request state."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class IssueState(str, Enum):
    """Issue state."""

    OPEN = "open"
    CLOSED = "closed"


class ReviewState(str, Enum):
    """Review state."""

    PENDING = "PENDING"
    COMMENTED = "COMMENTED"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    DISMISSED = "DISMISSED"


class GitHubConfig(BaseModel):
    """GitHub integration configuration."""

    token: str = Field(..., description="GitHub personal access token")
    base_url: str = Field(
        default="https://api.github.com", description="GitHub API base URL"
    )
    enterprise_url: str | None = Field(None, description="GitHub Enterprise URL")
    webhook_secret: str | None = Field(
        None, description="Webhook secret for verification"
    )
    default_owner: str | None = Field(None, description="Default repository owner")
    default_repo: str | None = Field(None, description="Default repository name")


class GitHubUser(BaseModel):
    """GitHub user model."""

    id: int
    login: str
    name: str | None = None
    email: str | None = None
    avatar_url: HttpUrl | None = None
    html_url: HttpUrl | None = None


class GitHubLabel(BaseModel):
    """GitHub label model."""

    id: int
    name: str
    color: str
    description: str | None = None


class GitHubMilestone(BaseModel):
    """GitHub milestone model."""

    id: int
    number: int
    title: str
    description: str | None = None
    state: str
    due_on: datetime | None = None
    open_issues: int = 0
    closed_issues: int = 0


class GitHubRepository(BaseModel):
    """GitHub repository model."""

    id: int
    name: str
    full_name: str
    description: str | None = None
    private: bool = False
    html_url: HttpUrl
    clone_url: str
    ssh_url: str
    default_branch: str = "main"
    language: str | None = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    owner: GitHubUser
    created_at: datetime
    updated_at: datetime


class GitHubComment(BaseModel):
    """GitHub comment model."""

    id: int
    body: str
    user: GitHubUser
    html_url: HttpUrl
    created_at: datetime
    updated_at: datetime
    path: str | None = None  # For review comments
    line: int | None = None  # For review comments
    commit_id: str | None = None


class GitHubReview(BaseModel):
    """GitHub pull request review model."""

    id: int
    user: GitHubUser
    body: str | None = None
    state: ReviewState
    html_url: HttpUrl
    submitted_at: datetime | None = None
    commit_id: str


class GitHubPullRequest(BaseModel):
    """GitHub pull request model."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: PullRequestState
    html_url: HttpUrl
    user: GitHubUser
    assignees: list[GitHubUser] = Field(default_factory=list)
    reviewers: list[GitHubUser] = Field(default_factory=list)
    labels: list[GitHubLabel] = Field(default_factory=list)
    milestone: GitHubMilestone | None = None
    head_ref: str
    base_ref: str
    head_sha: str
    base_sha: str
    mergeable: bool | None = None
    merged: bool = False
    merged_at: datetime | None = None
    merged_by: GitHubUser | None = None
    draft: bool = False
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: IssueState
    html_url: HttpUrl
    user: GitHubUser
    assignees: list[GitHubUser] = Field(default_factory=list)
    labels: list[GitHubLabel] = Field(default_factory=list)
    milestone: GitHubMilestone | None = None
    locked: bool = False
    comments: int = 0
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    closed_by: GitHubUser | None = None
