"""
APEX Development Platform - Linear Models
Phase 4: UI, Integrations & Analytics

Pydantic models for Linear API entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class IssuePriority(int, Enum):
    """Issue priority levels."""

    NO_PRIORITY = 0
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class IssueState(str, Enum):
    """Issue workflow states."""

    BACKLOG = "backlog"
    TODO = "triage"
    IN_PROGRESS = "started"
    IN_REVIEW = "review"
    DONE = "completed"
    CANCELLED = "canceled"


class LinearConfig(BaseModel):
    """Linear integration configuration."""

    api_key: str = Field(..., description="Linear API key")
    base_url: str = Field(default="https://api.linear.app/graphql", description="Linear GraphQL API URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook signing secret")
    default_team_id: Optional[str] = Field(None, description="Default team ID")


class LinearUser(BaseModel):
    """Linear user model."""

    id: str
    name: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    active: bool = True
    admin: bool = False


class LinearLabel(BaseModel):
    """Linear label model."""

    id: str
    name: str
    color: str
    description: Optional[str] = None


class LinearCycle(BaseModel):
    """Linear cycle model."""

    id: str
    number: int
    name: Optional[str] = None
    starts_at: datetime
    ends_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0


class LinearProject(BaseModel):
    """Linear project model."""

    id: str
    name: str
    description: Optional[str] = None
    slug_id: str
    icon: Optional[str] = None
    color: Optional[str] = None
    state: str = "planned"
    progress: float = 0.0
    target_date: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LinearTeam(BaseModel):
    """Linear team model."""

    id: str
    key: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    private: bool = False
    timezone: Optional[str] = None


class LinearComment(BaseModel):
    """Linear comment model."""

    id: str
    body: str
    user: Optional[LinearUser] = None
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime] = None


class LinearIssue(BaseModel):
    """Linear issue model."""

    id: str
    identifier: str  # e.g., "TEAM-123"
    title: str
    description: Optional[str] = None
    priority: IssuePriority = IssuePriority.NO_PRIORITY
    priority_label: str = "No priority"
    url: HttpUrl
    state: Optional[dict] = None  # Contains id, name, type
    assignee: Optional[LinearUser] = None
    creator: Optional[LinearUser] = None
    team: Optional[LinearTeam] = None
    project: Optional[LinearProject] = None
    cycle: Optional[LinearCycle] = None
    labels: list[LinearLabel] = Field(default_factory=list)
    parent: Optional["LinearIssue"] = None
    estimate: Optional[float] = None
    due_date: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
