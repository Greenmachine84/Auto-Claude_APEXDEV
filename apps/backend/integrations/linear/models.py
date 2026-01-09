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
    base_url: str = Field(
        default="https://api.linear.app/graphql", description="Linear GraphQL API URL"
    )
    webhook_secret: str | None = Field(None, description="Webhook signing secret")
    default_team_id: str | None = Field(None, description="Default team ID")


class LinearUser(BaseModel):
    """Linear user model."""

    id: str
    name: str
    email: str
    display_name: str | None = None
    avatar_url: HttpUrl | None = None
    active: bool = True
    admin: bool = False


class LinearLabel(BaseModel):
    """Linear label model."""

    id: str
    name: str
    color: str
    description: str | None = None


class LinearCycle(BaseModel):
    """Linear cycle model."""

    id: str
    number: int
    name: str | None = None
    starts_at: datetime
    ends_at: datetime
    completed_at: datetime | None = None
    progress: float = 0.0


class LinearProject(BaseModel):
    """Linear project model."""

    id: str
    name: str
    description: str | None = None
    slug_id: str
    icon: str | None = None
    color: str | None = None
    state: str = "planned"
    progress: float = 0.0
    target_date: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class LinearTeam(BaseModel):
    """Linear team model."""

    id: str
    key: str
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    private: bool = False
    timezone: str | None = None


class LinearComment(BaseModel):
    """Linear comment model."""

    id: str
    body: str
    user: LinearUser | None = None
    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None = None


class LinearIssue(BaseModel):
    """Linear issue model."""

    id: str
    identifier: str  # e.g., "TEAM-123"
    title: str
    description: str | None = None
    priority: IssuePriority = IssuePriority.NO_PRIORITY
    priority_label: str = "No priority"
    url: HttpUrl
    state: dict | None = None  # Contains id, name, type
    assignee: LinearUser | None = None
    creator: LinearUser | None = None
    team: LinearTeam | None = None
    project: LinearProject | None = None
    cycle: LinearCycle | None = None
    labels: list[LinearLabel] = Field(default_factory=list)
    parent: Optional["LinearIssue"] = None
    estimate: float | None = None
    due_date: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
