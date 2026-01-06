"""
APEX Development Platform - GitHub Models
Phase 4: UI, Integrations & Analytics

Pydantic models for GitHub API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

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
    base_url: str = Field(default="https://api.github.com", description="GitHub API base URL")
    enterprise_url: Optional[str] = Field(None, description="GitHub Enterprise URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret for verification")
    default_owner: Optional[str] = Field(None, description="Default repository owner")
    default_repo: Optional[str] = Field(None, description="Default repository name")


class GitHubUser(BaseModel):
    """GitHub user model."""

    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    html_url: Optional[HttpUrl] = None


class GitHubLabel(BaseModel):
    """GitHub label model."""

    id: int
    name: str
    color: str
    description: Optional[str] = None


class GitHubMilestone(BaseModel):
    """GitHub milestone model."""

    id: int
    number: int
    title: str
    description: Optional[str] = None
    state: str
    due_on: Optional[datetime] = None
    open_issues: int = 0
    closed_issues: int = 0


class GitHubRepository(BaseModel):
    """GitHub repository model."""

    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool = False
    html_url: HttpUrl
    clone_url: str
    ssh_url: str
    default_branch: str = "main"
    language: Optional[str] = None
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
    path: Optional[str] = None  # For review comments
    line: Optional[int] = None  # For review comments
    commit_id: Optional[str] = None


class GitHubReview(BaseModel):
    """GitHub pull request review model."""

    id: int
    user: GitHubUser
    body: Optional[str] = None
    state: ReviewState
    html_url: HttpUrl
    submitted_at: Optional[datetime] = None
    commit_id: str


class GitHubPullRequest(BaseModel):
    """GitHub pull request model."""

    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: PullRequestState
    html_url: HttpUrl
    user: GitHubUser
    assignees: list[GitHubUser] = Field(default_factory=list)
    reviewers: list[GitHubUser] = Field(default_factory=list)
    labels: list[GitHubLabel] = Field(default_factory=list)
    milestone: Optional[GitHubMilestone] = None
    head_ref: str
    base_ref: str
    head_sha: str
    base_sha: str
    mergeable: Optional[bool] = None
    merged: bool = False
    merged_at: Optional[datetime] = None
    merged_by: Optional[GitHubUser] = None
    draft: bool = False
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: IssueState
    html_url: HttpUrl
    user: GitHubUser
    assignees: list[GitHubUser] = Field(default_factory=list)
    labels: list[GitHubLabel] = Field(default_factory=list)
    milestone: Optional[GitHubMilestone] = None
    locked: bool = False
    comments: int = 0
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    closed_by: Optional[GitHubUser] = None
