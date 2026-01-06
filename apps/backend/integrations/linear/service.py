"""
APEX Development Platform - Linear Service
Phase 4: UI, Integrations & Analytics

High-level service for Linear operations.
"""

import logging
from typing import Optional

from .client import LinearClient
from .models import (
    LinearConfig,
    LinearComment,
    LinearIssue,
    LinearProject,
    LinearTeam,
    LinearUser,
    IssuePriority,
)

logger = logging.getLogger(__name__)


class LinearService:
    """High-level Linear service."""

    def __init__(self, config: LinearConfig):
        self.config = config
        self.client = LinearClient(config)
        self._team_id = config.default_team_id

    async def close(self) -> None:
        """Close service."""
        await self.client.close()

    def _convert_issue(self, data: dict) -> LinearIssue:
        """Convert GraphQL response to LinearIssue."""
        # Handle labels nodes
        labels_data = data.get("labels", {})
        labels = labels_data.get("nodes", []) if isinstance(labels_data, dict) else []

        return LinearIssue(
            id=data["id"],
            identifier=data["identifier"],
            title=data["title"],
            description=data.get("description"),
            priority=IssuePriority(data.get("priority", 0)),
            priority_label=data.get("priorityLabel", "No priority"),
            url=data["url"],
            state=data.get("state"),
            assignee=LinearUser(**data["assignee"]) if data.get("assignee") else None,
            creator=LinearUser(**data["creator"]) if data.get("creator") else None,
            team=LinearTeam(**data["team"]) if data.get("team") else None,
            project=LinearProject(**data["project"]) if data.get("project") else None,
            labels=labels,
            estimate=data.get("estimate"),
            due_date=data.get("dueDate"),
            started_at=data.get("startedAt"),
            completed_at=data.get("completedAt"),
            cancelled_at=data.get("cancelledAt"),
            created_at=data["createdAt"],
            updated_at=data["updatedAt"],
            archived_at=data.get("archivedAt"),
        )

    # User methods
    async def get_viewer(self) -> LinearUser:
        """Get authenticated user."""
        query = f"""
            {self.client.USER_FRAGMENT}
            query {{ viewer {{ ...UserFields }} }}
        """
        data = await self.client.query(query)
        return LinearUser(**data["viewer"])

    # Team methods
    async def list_teams(self) -> list[LinearTeam]:
        """List teams."""
        query = """
            query {
                teams { nodes { id key name description icon color private timezone } }
            }
        """
        data = await self.client.query(query)
        return [LinearTeam(**t) for t in data["teams"]["nodes"]]

    async def get_team(self, team_id: Optional[str] = None) -> LinearTeam:
        """Get team by ID."""
        tid = team_id or self._team_id
        if not tid:
            raise ValueError("Team ID must be specified")
        query = """
            query($id: String!) {
                team(id: $id) { id key name description icon color private timezone }
            }
        """
        data = await self.client.query(query, {"id": tid})
        return LinearTeam(**data["team"])

    # Project methods
    async def list_projects(self, team_id: Optional[str] = None) -> list[LinearProject]:
        """List projects."""
        query = f"""
            {self.client.PROJECT_FRAGMENT}
            query($teamId: String) {{
                projects(filter: {{ team: {{ id: {{ eq: $teamId }} }} }}) {{
                    nodes {{ ...ProjectFields }}
                }}
            }}
        """
        tid = team_id or self._team_id
        data = await self.client.query(query, {"teamId": tid} if tid else {})
        return [LinearProject(**p) for p in data["projects"]["nodes"]]

    async def get_project(self, project_id: str) -> LinearProject:
        """Get project by ID."""
        query = f"""
            {self.client.PROJECT_FRAGMENT}
            query($id: String!) {{
                project(id: $id) {{ ...ProjectFields }}
            }}
        """
        data = await self.client.query(query, {"id": project_id})
        return LinearProject(**data["project"])

    # Issue methods
    async def list_issues(
        self,
        team_id: Optional[str] = None,
        project_id: Optional[str] = None,
        state_names: Optional[list[str]] = None,
        first: int = 50,
    ) -> list[LinearIssue]:
        """List issues."""
        query = f"""
            {self.client.USER_FRAGMENT}
            {self.client.LABEL_FRAGMENT}
            {self.client.ISSUE_FRAGMENT}
            query($filter: IssueFilter, $first: Int) {{
                issues(filter: $filter, first: $first) {{
                    nodes {{ ...IssueFields }}
                }}
            }}
        """
        filter_obj = {}
        tid = team_id or self._team_id
        if tid:
            filter_obj["team"] = {"id": {"eq": tid}}
        if project_id:
            filter_obj["project"] = {"id": {"eq": project_id}}
        if state_names:
            filter_obj["state"] = {"name": {"in": state_names}}

        data = await self.client.query(query, {"filter": filter_obj, "first": first})
        return [self._convert_issue(i) for i in data["issues"]["nodes"]]

    async def get_issue(self, issue_id: str) -> LinearIssue:
        """Get issue by ID."""
        query = f"""
            {self.client.USER_FRAGMENT}
            {self.client.LABEL_FRAGMENT}
            {self.client.ISSUE_FRAGMENT}
            query($id: String!) {{
                issue(id: $id) {{ ...IssueFields }}
            }}
        """
        data = await self.client.query(query, {"id": issue_id})
        return self._convert_issue(data["issue"])

    async def create_issue(
        self,
        title: str,
        description: Optional[str] = None,
        team_id: Optional[str] = None,
        project_id: Optional[str] = None,
        priority: Optional[IssuePriority] = None,
        assignee_id: Optional[str] = None,
        label_ids: Optional[list[str]] = None,
        estimate: Optional[float] = None,
    ) -> LinearIssue:
        """Create issue."""
        tid = team_id or self._team_id
        if not tid:
            raise ValueError("Team ID must be specified")

        mutation = f"""
            {self.client.USER_FRAGMENT}
            {self.client.LABEL_FRAGMENT}
            {self.client.ISSUE_FRAGMENT}
            mutation($input: IssueCreateInput!) {{
                issueCreate(input: $input) {{
                    success
                    issue {{ ...IssueFields }}
                }}
            }}
        """
        input_obj = {"title": title, "teamId": tid}
        if description:
            input_obj["description"] = description
        if project_id:
            input_obj["projectId"] = project_id
        if priority is not None:
            input_obj["priority"] = priority.value
        if assignee_id:
            input_obj["assigneeId"] = assignee_id
        if label_ids:
            input_obj["labelIds"] = label_ids
        if estimate is not None:
            input_obj["estimate"] = estimate

        data = await self.client.mutate(mutation, {"input": input_obj})
        return self._convert_issue(data["issueCreate"]["issue"])

    async def update_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[IssuePriority] = None,
        state_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> LinearIssue:
        """Update issue."""
        mutation = f"""
            {self.client.USER_FRAGMENT}
            {self.client.LABEL_FRAGMENT}
            {self.client.ISSUE_FRAGMENT}
            mutation($id: String!, $input: IssueUpdateInput!) {{
                issueUpdate(id: $id, input: $input) {{
                    success
                    issue {{ ...IssueFields }}
                }}
            }}
        """
        input_obj = {}
        if title:
            input_obj["title"] = title
        if description:
            input_obj["description"] = description
        if priority is not None:
            input_obj["priority"] = priority.value
        if state_id:
            input_obj["stateId"] = state_id
        if assignee_id:
            input_obj["assigneeId"] = assignee_id

        data = await self.client.mutate(mutation, {"id": issue_id, "input": input_obj})
        return self._convert_issue(data["issueUpdate"]["issue"])

    # Comment methods
    async def list_issue_comments(self, issue_id: str) -> list[LinearComment]:
        """List issue comments."""
        query = f"""
            {self.client.USER_FRAGMENT}
            query($id: String!) {{
                issue(id: $id) {{
                    comments {{
                        nodes {{
                            id
                            body
                            user {{ ...UserFields }}
                            createdAt
                            updatedAt
                            editedAt
                        }}
                    }}
                }}
            }}
        """
        data = await self.client.query(query, {"id": issue_id})
        comments = data["issue"]["comments"]["nodes"]
        return [
            LinearComment(
                id=c["id"],
                body=c["body"],
                user=LinearUser(**c["user"]) if c.get("user") else None,
                created_at=c["createdAt"],
                updated_at=c["updatedAt"],
                edited_at=c.get("editedAt"),
            )
            for c in comments
        ]

    async def create_issue_comment(
        self,
        issue_id: str,
        body: str,
    ) -> LinearComment:
        """Create issue comment."""
        mutation = """
            mutation($input: CommentCreateInput!) {
                commentCreate(input: $input) {
                    success
                    comment {
                        id
                        body
                        createdAt
                        updatedAt
                    }
                }
            }
        """
        data = await self.client.mutate(mutation, {"input": {"issueId": issue_id, "body": body}})
        c = data["commentCreate"]["comment"]
        return LinearComment(
            id=c["id"],
            body=c["body"],
            created_at=c["createdAt"],
            updated_at=c["updatedAt"],
        )
