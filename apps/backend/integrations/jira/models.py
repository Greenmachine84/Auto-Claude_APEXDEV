"""
APEX Development Platform - JIRA Models
Phase 4: UI, Integrations & Analytics

Pydantic models for JIRA API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

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

    base_url: str = Field(..., description="JIRA instance URL (e.g., https://company.atlassian.net)")
    email: str = Field(..., description="JIRA user email")
    api_token: str = Field(..., description="JIRA API token")
    project_key: Optional[str] = Field(None, description="Default project key")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret")


class JiraUser(BaseModel):
    """JIRA user model."""

    account_id: str
    display_name: str
    email_address: Optional[str] = None
    avatar_urls: Optional[dict[str, str]] = None
    active: bool = True
    time_zone: Optional[str] = None


class JiraStatus(BaseModel):
    """JIRA status model."""

    id: str
    name: str
    description: Optional[str] = None
    category_key: str = "undefined"  # todo, indeterminate, done
    icon_url: Optional[str] = None


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
    board_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    complete_date: Optional[datetime] = None
    goal: Optional[str] = None


class JiraProject(BaseModel):
    """JIRA project model."""

    id: str
    key: str
    name: str
    description: Optional[str] = None
    lead: Optional[JiraUser] = None
    url: Optional[HttpUrl] = None
    project_type_key: str = "software"
    avatar_urls: Optional[dict[str, str]] = None
    category: Optional[dict] = None


class JiraComment(BaseModel):
    """JIRA comment model."""

    id: str
    body: str  # Can be ADF (Atlassian Document Format) or plain text
    author: JiraUser
    created: datetime
    updated: datetime
    visibility: Optional[dict] = None


class JiraIssue(BaseModel):
    """JIRA issue model."""

    id: str
    key: str  # e.g., "PROJ-123"
    self_url: Optional[HttpUrl] = Field(None, alias="self")
    summary: str
    description: Optional[str] = None
    issue_type: str
    status: JiraStatus
    priority: Optional[str] = None
    assignee: Optional[JiraUser] = None
    reporter: Optional[JiraUser] = None
    creator: Optional[JiraUser] = None
    project: Optional[JiraProject] = None
    parent: Optional["JiraIssue"] = None
    subtasks: list["JiraIssue"] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    components: list[dict] = Field(default_factory=list)
    fix_versions: list[dict] = Field(default_factory=list)
    sprint: Optional[JiraSprint] = None
    story_points: Optional[float] = None
    created: datetime
    updated: datetime
    resolved: Optional[datetime] = None
    due_date: Optional[str] = None
    comments: list[JiraComment] = Field(default_factory=list)

    class Config:
        populate_by_name = True
