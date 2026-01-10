"""
APEX Development Platform - GitLab Models
Phase 4: UI, Integrations & Analytics

Pydantic models for GitLab API entities.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class MergeRequestState(str, Enum):
    """Merge request state."""

    OPENED = "opened"
    CLOSED = "closed"
    MERGED = "merged"
    LOCKED = "locked"


class IssueState(str, Enum):
    """Issue state."""

    OPENED = "opened"
    CLOSED = "closed"


class GitLabConfig(BaseModel):
    """GitLab integration configuration."""

    token: str = Field(..., description="GitLab personal access token")
    base_url: str = Field(
        default="https://gitlab.com/api/v4", description="GitLab API base URL"
    )
    webhook_secret: str | None = Field(
        None, description="Webhook secret for verification"
    )
    default_project_id: int | None = Field(None, description="Default project ID")


class GitLabUser(BaseModel):
    """GitLab user model."""

    id: int
    username: str
    name: str
    email: str | None = None
    avatar_url: HttpUrl | None = None
    web_url: HttpUrl | None = None
    state: str = "active"


class GitLabLabel(BaseModel):
    """GitLab label model."""

    id: int
    name: str
    color: str
    description: str | None = None
    text_color: str = "#FFFFFF"


class GitLabMilestone(BaseModel):
    """GitLab milestone model."""

    id: int
    iid: int
    title: str
    description: str | None = None
    state: str
    due_date: str | None = None
    start_date: str | None = None
    web_url: HttpUrl | None = None


class GitLabProject(BaseModel):
    """GitLab project model."""

    id: int
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    description: str | None = None
    visibility: str = "private"
    web_url: HttpUrl
    ssh_url_to_repo: str
    http_url_to_repo: str
    default_branch: str = "main"
    star_count: int = 0
    forks_count: int = 0
    open_issues_count: int | None = None
    created_at: datetime
    last_activity_at: datetime
    owner: GitLabUser | None = None
    namespace: dict | None = None


class GitLabNote(BaseModel):
    """GitLab note (comment) model."""

    id: int
    body: str
    author: GitLabUser
    created_at: datetime
    updated_at: datetime
    system: bool = False
    noteable_type: str | None = None
    noteable_id: int | None = None
    resolvable: bool = False
    resolved: bool = False
    resolved_by: GitLabUser | None = None


class GitLabMergeRequest(BaseModel):
    """GitLab merge request model."""

    id: int
    iid: int
    title: str
    description: str | None = None
    state: MergeRequestState
    web_url: HttpUrl
    author: GitLabUser
    assignees: list[GitLabUser] = Field(default_factory=list)
    reviewers: list[GitLabUser] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    milestone: GitLabMilestone | None = None
    source_branch: str
    target_branch: str
    source_project_id: int
    target_project_id: int
    sha: str
    merge_commit_sha: str | None = None
    squash_commit_sha: str | None = None
    has_conflicts: bool = False
    blocking_discussions_resolved: bool = True
    work_in_progress: bool = False
    draft: bool = False
    merged_at: datetime | None = None
    merged_by: GitLabUser | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    changes_count: str | None = None
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0


class GitLabIssue(BaseModel):
    """GitLab issue model."""

    id: int
    iid: int
    title: str
    description: str | None = None
    state: IssueState
    web_url: HttpUrl
    author: GitLabUser
    assignees: list[GitLabUser] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    milestone: GitLabMilestone | None = None
    confidential: bool = False
    due_date: str | None = None
    weight: int | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    closed_by: GitLabUser | None = None
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0
