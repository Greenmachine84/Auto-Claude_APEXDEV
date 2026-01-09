"""
APEX Development Platform - JIRA Service
Phase 4: UI, Integrations & Analytics

High-level service for JIRA operations.
"""

import logging
from typing import Any

from .client import JiraClient
from .models import (
    IssuePriority,
    IssueType,
    JiraComment,
    JiraConfig,
    JiraIssue,
    JiraProject,
    JiraStatus,
    JiraTransition,
    JiraUser,
)

logger = logging.getLogger(__name__)


class JiraService:
    """High-level JIRA service."""

    def __init__(self, config: JiraConfig):
        self.config = config
        self.client = JiraClient(config)
        self._project_key = config.project_key

    async def close(self) -> None:
        """Close service."""
        await self.client.close()

    def _parse_user(self, data: dict | None) -> JiraUser | None:
        """Parse user from API response."""
        if not data:
            return None
        return JiraUser(
            account_id=data.get("accountId", ""),
            display_name=data.get("displayName", ""),
            email_address=data.get("emailAddress"),
            avatar_urls=data.get("avatarUrls"),
            active=data.get("active", True),
            time_zone=data.get("timeZone"),
        )

    def _parse_status(self, data: dict) -> JiraStatus:
        """Parse status from API response."""
        return JiraStatus(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            category_key=data.get("statusCategory", {}).get("key", "undefined"),
            icon_url=data.get("iconUrl"),
        )

    def _parse_issue(self, data: dict) -> JiraIssue:
        """Parse issue from API response."""
        fields = data.get("fields", {})
        return JiraIssue(
            id=data.get("id", ""),
            key=data.get("key", ""),
            self_url=data.get("self"),
            summary=fields.get("summary", ""),
            description=self._extract_description(fields.get("description")),
            issue_type=fields.get("issuetype", {}).get("name", ""),
            status=self._parse_status(fields.get("status", {})),
            priority=fields.get("priority", {}).get("name")
            if fields.get("priority")
            else None,
            assignee=self._parse_user(fields.get("assignee")),
            reporter=self._parse_user(fields.get("reporter")),
            creator=self._parse_user(fields.get("creator")),
            labels=fields.get("labels", []),
            components=fields.get("components", []),
            fix_versions=fields.get("fixVersions", []),
            created=fields.get("created"),
            updated=fields.get("updated"),
            resolved=fields.get("resolutiondate"),
            due_date=fields.get("duedate"),
        )

    def _extract_description(self, desc: Any) -> str | None:
        """Extract plain text from ADF or return as-is."""
        if desc is None:
            return None
        if isinstance(desc, str):
            return desc
        # Handle Atlassian Document Format (simplified)
        if isinstance(desc, dict) and "content" in desc:
            texts = []
            for block in desc.get("content", []):
                if block.get("type") == "paragraph":
                    for item in block.get("content", []):
                        if item.get("type") == "text":
                            texts.append(item.get("text", ""))
            return "\n".join(texts)
        return str(desc)

    # User methods
    async def get_myself(self) -> JiraUser:
        """Get current user."""
        data = await self.client.get("/myself")
        return self._parse_user(data)  # type: ignore

    # Project methods
    async def list_projects(self) -> list[JiraProject]:
        """List accessible projects."""
        data = await self.client.get("/project")
        return [
            JiraProject(
                id=p.get("id", ""),
                key=p.get("key", ""),
                name=p.get("name", ""),
                description=p.get("description"),
                project_type_key=p.get("projectTypeKey", "software"),
                avatar_urls=p.get("avatarUrls"),
            )
            for p in data
        ]

    async def get_project(self, project_key: str | None = None) -> JiraProject:
        """Get project details."""
        key = project_key or self._project_key
        if not key:
            raise ValueError("Project key must be specified")
        data = await self.client.get(f"/project/{key}")
        return JiraProject(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            lead=self._parse_user(data.get("lead")),
            project_type_key=data.get("projectTypeKey", "software"),
            avatar_urls=data.get("avatarUrls"),
        )

    # Issue methods
    async def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> list[JiraIssue]:
        """Search issues using JQL."""
        data = await self.client.search_issues(jql, max_results=max_results)
        return [self._parse_issue(i) for i in data.get("issues", [])]

    async def list_project_issues(
        self,
        project_key: str | None = None,
        issue_type: IssueType | None = None,
        status: str | None = None,
        max_results: int = 50,
    ) -> list[JiraIssue]:
        """List issues in project."""
        key = project_key or self._project_key
        if not key:
            raise ValueError("Project key must be specified")

        jql_parts = [f"project = {key}"]
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type.value}"')
        if status:
            jql_parts.append(f'status = "{status}"')
        jql_parts.append("ORDER BY created DESC")

        return await self.search_issues(" AND ".join(jql_parts), max_results)

    async def get_issue(self, issue_key: str) -> JiraIssue:
        """Get issue details."""
        data = await self.client.get(f"/issue/{issue_key}")
        return self._parse_issue(data)

    async def create_issue(
        self,
        summary: str,
        issue_type: IssueType = IssueType.TASK,
        description: str | None = None,
        priority: IssuePriority | None = None,
        assignee_id: str | None = None,
        labels: list[str] | None = None,
        project_key: str | None = None,
    ) -> JiraIssue:
        """Create issue."""
        key = project_key or self._project_key
        if not key:
            raise ValueError("Project key must be specified")

        fields: dict[str, Any] = {
            "project": {"key": key},
            "summary": summary,
            "issuetype": {"name": issue_type.value},
        }
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }
        if priority:
            fields["priority"] = {"name": priority.value}
        if assignee_id:
            fields["assignee"] = {"accountId": assignee_id}
        if labels:
            fields["labels"] = labels

        data = await self.client.post("/issue", json={"fields": fields})
        return await self.get_issue(data["key"])

    async def update_issue(
        self,
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
        priority: IssuePriority | None = None,
        assignee_id: str | None = None,
        labels: list[str] | None = None,
    ) -> JiraIssue:
        """Update issue."""
        fields: dict[str, Any] = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }
        if priority:
            fields["priority"] = {"name": priority.value}
        if assignee_id:
            fields["assignee"] = {"accountId": assignee_id}
        if labels is not None:
            fields["labels"] = labels

        await self.client.put(f"/issue/{issue_key}", json={"fields": fields})
        return await self.get_issue(issue_key)

    # Transition methods
    async def get_transitions(self, issue_key: str) -> list[JiraTransition]:
        """Get available transitions for issue."""
        data = await self.client.get(f"/issue/{issue_key}/transitions")
        return [
            JiraTransition(
                id=t.get("id", ""),
                name=t.get("name", ""),
                to=self._parse_status(t.get("to", {})),
                has_screen=t.get("hasScreen", False),
                is_global=t.get("isGlobal", False),
                is_initial=t.get("isInitial", False),
                is_available=t.get("isAvailable", True),
            )
            for t in data.get("transitions", [])
        ]

    async def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: str | None = None,
    ) -> JiraIssue:
        """Transition issue to new status."""
        payload: dict[str, Any] = {"transition": {"id": transition_id}}
        if comment:
            payload["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": comment}],
                                    }
                                ],
                            }
                        }
                    }
                ]
            }
        await self.client.post(f"/issue/{issue_key}/transitions", json=payload)
        return await self.get_issue(issue_key)

    # Comment methods
    async def list_comments(self, issue_key: str) -> list[JiraComment]:
        """List issue comments."""
        data = await self.client.get(f"/issue/{issue_key}/comment")
        return [
            JiraComment(
                id=c.get("id", ""),
                body=self._extract_description(c.get("body")) or "",
                author=self._parse_user(c.get("author")),  # type: ignore
                created=c.get("created"),
                updated=c.get("updated"),
                visibility=c.get("visibility"),
            )
            for c in data.get("comments", [])
        ]

    async def add_comment(self, issue_key: str, body: str) -> JiraComment:
        """Add comment to issue."""
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body}],
                    }
                ],
            }
        }
        data = await self.client.post(f"/issue/{issue_key}/comment", json=payload)
        return JiraComment(
            id=data.get("id", ""),
            body=body,
            author=self._parse_user(data.get("author")),  # type: ignore
            created=data.get("created"),
            updated=data.get("updated"),
        )
