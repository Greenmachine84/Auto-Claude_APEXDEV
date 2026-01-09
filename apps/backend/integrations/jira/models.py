"""
APEX Development Platform - JIRA Models
Phase 4: UI, Integrations & Analytics

Pydantic models for JIRA API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class IssueType(str, Enum):
    """JIRA issue types."""

    EPIC = "Epic"
    STORY = "Story"
    TASK = "Task"
    SUBTASK = "Sub-task"
    BUG = "Bug"
    IMPROVEMENT = "Improvement"
    FEATURE = "Feature"


class IssuePriority(str, Enum):
    """JIRA issue priorities."""

    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"


class JiraConfig(BaseModel):
    """JIRA integration configuration."""

    base_url: str = Field(
        ..., description="JIRA instance URL (e.g., https://company.atlassian.net)"
    )
    email: str = Field(..., description="JIRA user email")
    api_token: str = Field(..., description="JIRA API token")
    project_key: str | None = Field(None, description="Default project key")
    webhook_secret: str | None = Field(None, description="Webhook secret")


class JiraUser(BaseModel):
    """JIRA user model."""

    account_id: str
    display_name: str
    email_address: str | None = None
    avatar_urls: dict[str, str] | None = None
    active: bool = True
    time_zone: str | None = None


class JiraStatus(BaseModel):
    """JIRA status model."""

    id: str
    name: str
    description: str | None = None
    category_key: str = "undefined"  # todo, indeterminate, done
    icon_url: str | None = None


class JiraTransition(BaseModel):
    """JIRA workflow transition."""

    id: str
    name: str
    to: JiraStatus
    has_screen: bool = False
    is_global: bool = False
    is_initial: bool = False
    is_available: bool = True


class JiraSprint(BaseModel):
    """JIRA sprint model."""

    id: int
    name: str
    state: str  # future, active, closed
    board_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    complete_date: datetime | None = None
    goal: str | None = None


class JiraProject(BaseModel):
    """JIRA project model."""

    id: str
    key: str
    name: str
    description: str | None = None
    lead: JiraUser | None = None
    url: HttpUrl | None = None
    project_type_key: str = "software"
    avatar_urls: dict[str, str] | None = None
    category: dict | None = None


class JiraComment(BaseModel):
    """JIRA comment model."""

    id: str
    body: str  # Can be ADF (Atlassian Document Format) or plain text
    author: JiraUser
    created: datetime
    updated: datetime
    visibility: dict | None = None


class JiraIssue(BaseModel):
    """JIRA issue model."""

    id: str
    key: str  # e.g., "PROJ-123"
    self_url: HttpUrl | None = Field(None, alias="self")
    summary: str
    description: str | None = None
    issue_type: str
    status: JiraStatus
    priority: str | None = None
    assignee: JiraUser | None = None
    reporter: JiraUser | None = None
    creator: JiraUser | None = None
    project: JiraProject | None = None
    parent: Optional["JiraIssue"] = None
    subtasks: list["JiraIssue"] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    components: list[dict] = Field(default_factory=list)
    fix_versions: list[dict] = Field(default_factory=list)
    sprint: JiraSprint | None = None
    story_points: float | None = None
    created: datetime
    updated: datetime
    resolved: datetime | None = None
    due_date: str | None = None
    comments: list[JiraComment] = Field(default_factory=list)

    class Config:
        populate_by_name = True
