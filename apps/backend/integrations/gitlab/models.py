"""
APEX Development Platform - GitLab Models
Phase 4: UI, Integrations & Analytics

Pydantic models for GitLab API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

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
    base_url: str = Field(default="https://gitlab.com/api/v4", description="GitLab API base URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret for verification")
    default_project_id: Optional[int] = Field(None, description="Default project ID")


class GitLabUser(BaseModel):
    """GitLab user model."""

    id: int
    username: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    web_url: Optional[HttpUrl] = None
    state: str = "active"


class GitLabLabel(BaseModel):
    """GitLab label model."""

    id: int
    name: str
    color: str
    description: Optional[str] = None
    text_color: str = "#FFFFFF"


class GitLabMilestone(BaseModel):
    """GitLab milestone model."""

    id: int
    iid: int
    title: str
    description: Optional[str] = None
    state: str
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    web_url: Optional[HttpUrl] = None


class GitLabProject(BaseModel):
    """GitLab project model."""

    id: int
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    description: Optional[str] = None
    visibility: str = "private"
    web_url: HttpUrl
    ssh_url_to_repo: str
    http_url_to_repo: str
    default_branch: str = "main"
    star_count: int = 0
    forks_count: int = 0
    open_issues_count: Optional[int] = None
    created_at: datetime
    last_activity_at: datetime
    owner: Optional[GitLabUser] = None
    namespace: Optional[dict] = None


class GitLabNote(BaseModel):
    """GitLab note (comment) model."""

    id: int
    body: str
    author: GitLabUser
    created_at: datetime
    updated_at: datetime
    system: bool = False
    noteable_type: Optional[str] = None
    noteable_id: Optional[int] = None
    resolvable: bool = False
    resolved: bool = False
    resolved_by: Optional[GitLabUser] = None


class GitLabMergeRequest(BaseModel):
    """GitLab merge request model."""

    id: int
    iid: int
    title: str
    description: Optional[str] = None
    state: MergeRequestState
    web_url: HttpUrl
    author: GitLabUser
    assignees: list[GitLabUser] = Field(default_factory=list)
    reviewers: list[GitLabUser] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    milestone: Optional[GitLabMilestone] = None
    source_branch: str
    target_branch: str
    source_project_id: int
    target_project_id: int
    sha: str
    merge_commit_sha: Optional[str] = None
    squash_commit_sha: Optional[str] = None
    has_conflicts: bool = False
    blocking_discussions_resolved: bool = True
    work_in_progress: bool = False
    draft: bool = False
    merged_at: Optional[datetime] = None
    merged_by: Optional[GitLabUser] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    changes_count: Optional[str] = None
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0


class GitLabIssue(BaseModel):
    """GitLab issue model."""

    id: int
    iid: int
    title: str
    description: Optional[str] = None
    state: IssueState
    web_url: HttpUrl
    author: GitLabUser
    assignees: list[GitLabUser] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    milestone: Optional[GitLabMilestone] = None
    confidential: bool = False
    due_date: Optional[str] = None
    weight: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    closed_by: Optional[GitLabUser] = None
    user_notes_count: int = 0
    upvotes: int = 0
    downvotes: int = 0
