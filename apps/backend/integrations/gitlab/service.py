"""
APEX Development Platform - GitLab Service
Phase 4: UI, Integrations & Analytics

High-level service for GitLab operations.
"""

import logging

from .client import GitLabClient
from .models import (
    GitLabConfig,
    GitLabIssue,
    GitLabMergeRequest,
    GitLabNote,
    GitLabProject,
    GitLabUser,
    IssueState,
    MergeRequestState,
)

logger = logging.getLogger(__name__)


class GitLabService:
    """High-level GitLab service."""

    def __init__(self, config: GitLabConfig):
        self.config = config
        self.client = GitLabClient(config)
        self._project_id = config.default_project_id

    def _project_path(self, project_id: int | str | None = None) -> str:
        """Build project path."""
        pid = project_id or self._project_id
        if not pid:
            raise ValueError("Project ID must be specified")
        encoded = self.client.encode_project_id(pid)
        return f"/projects/{encoded}"

    async def close(self) -> None:
        """Close service."""
        await self.client.close()

    # User methods
    async def get_current_user(self) -> GitLabUser:
        """Get current authenticated user."""
        data = await self.client.get("/user")
        return GitLabUser(**data)

    # Project methods
    async def get_project(
        self, project_id: int | str | None = None
    ) -> GitLabProject:
        """Get project details."""
        path = self._project_path(project_id)
        data = await self.client.get(path)
        return GitLabProject(**data)

    async def list_projects(
        self,
        membership: bool = True,
        owned: bool = False,
    ) -> list[GitLabProject]:
        """List projects."""
        params = {}
        if membership:
            params["membership"] = "true"
        if owned:
            params["owned"] = "true"
        data = await self.client.paginate("/projects", params)
        return [GitLabProject(**p) for p in data]

    # Merge request methods
    async def list_merge_requests(
        self,
        project_id: int | str | None = None,
        state: MergeRequestState = MergeRequestState.OPENED,
    ) -> list[GitLabMergeRequest]:
        """List merge requests."""
        path = f"{self._project_path(project_id)}/merge_requests"
        data = await self.client.paginate(path, {"state": state.value})
        return [GitLabMergeRequest(**mr) for mr in data]

    async def get_merge_request(
        self,
        iid: int,
        project_id: int | str | None = None,
    ) -> GitLabMergeRequest:
        """Get merge request details."""
        path = f"{self._project_path(project_id)}/merge_requests/{iid}"
        data = await self.client.get(path)
        return GitLabMergeRequest(**data)

    async def create_merge_request(
        self,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str | None = None,
        draft: bool = False,
        project_id: int | str | None = None,
    ) -> GitLabMergeRequest:
        """Create merge request."""
        path = f"{self._project_path(project_id)}/merge_requests"
        payload = {
            "title": f"Draft: {title}" if draft else title,
            "source_branch": source_branch,
            "target_branch": target_branch,
        }
        if description:
            payload["description"] = description
        data = await self.client.post(path, json=payload)
        return GitLabMergeRequest(**data)

    async def update_merge_request(
        self,
        iid: int,
        title: str | None = None,
        description: str | None = None,
        state_event: str | None = None,  # 'close' or 'reopen'
        project_id: int | str | None = None,
    ) -> GitLabMergeRequest:
        """Update merge request."""
        path = f"{self._project_path(project_id)}/merge_requests/{iid}"
        payload = {}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if state_event:
            payload["state_event"] = state_event
        data = await self.client.put(path, json=payload)
        return GitLabMergeRequest(**data)

    async def merge_merge_request(
        self,
        iid: int,
        merge_commit_message: str | None = None,
        squash: bool = False,
        should_remove_source_branch: bool = False,
        project_id: int | str | None = None,
    ) -> GitLabMergeRequest:
        """Accept and merge a merge request."""
        path = f"{self._project_path(project_id)}/merge_requests/{iid}/merge"
        payload = {
            "squash": squash,
            "should_remove_source_branch": should_remove_source_branch,
        }
        if merge_commit_message:
            payload["merge_commit_message"] = merge_commit_message
        data = await self.client.put(path, json=payload)
        return GitLabMergeRequest(**data)

    # Issue methods
    async def list_issues(
        self,
        project_id: int | str | None = None,
        state: IssueState = IssueState.OPENED,
        labels: list[str] | None = None,
    ) -> list[GitLabIssue]:
        """List issues."""
        path = f"{self._project_path(project_id)}/issues"
        params = {"state": state.value}
        if labels:
            params["labels"] = ",".join(labels)
        data = await self.client.paginate(path, params)
        return [GitLabIssue(**i) for i in data]

    async def get_issue(
        self,
        iid: int,
        project_id: int | str | None = None,
    ) -> GitLabIssue:
        """Get issue details."""
        path = f"{self._project_path(project_id)}/issues/{iid}"
        data = await self.client.get(path)
        return GitLabIssue(**data)

    async def create_issue(
        self,
        title: str,
        description: str | None = None,
        labels: list[str] | None = None,
        assignee_ids: list[int] | None = None,
        project_id: int | str | None = None,
    ) -> GitLabIssue:
        """Create issue."""
        path = f"{self._project_path(project_id)}/issues"
        payload = {"title": title}
        if description:
            payload["description"] = description
        if labels:
            payload["labels"] = ",".join(labels)
        if assignee_ids:
            payload["assignee_ids"] = assignee_ids
        data = await self.client.post(path, json=payload)
        return GitLabIssue(**data)

    async def update_issue(
        self,
        iid: int,
        title: str | None = None,
        description: str | None = None,
        state_event: str | None = None,  # 'close' or 'reopen'
        labels: list[str] | None = None,
        project_id: int | str | None = None,
    ) -> GitLabIssue:
        """Update issue."""
        path = f"{self._project_path(project_id)}/issues/{iid}"
        payload = {}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if state_event:
            payload["state_event"] = state_event
        if labels is not None:
            payload["labels"] = ",".join(labels)
        data = await self.client.put(path, json=payload)
        return GitLabIssue(**data)

    # Note (comment) methods
    async def list_merge_request_notes(
        self,
        iid: int,
        project_id: int | str | None = None,
    ) -> list[GitLabNote]:
        """List merge request notes."""
        path = f"{self._project_path(project_id)}/merge_requests/{iid}/notes"
        data = await self.client.get(path)
        return [GitLabNote(**n) for n in data]

    async def create_merge_request_note(
        self,
        iid: int,
        body: str,
        project_id: int | str | None = None,
    ) -> GitLabNote:
        """Create merge request note."""
        path = f"{self._project_path(project_id)}/merge_requests/{iid}/notes"
        data = await self.client.post(path, json={"body": body})
        return GitLabNote(**data)

    async def list_issue_notes(
        self,
        iid: int,
        project_id: int | str | None = None,
    ) -> list[GitLabNote]:
        """List issue notes."""
        path = f"{self._project_path(project_id)}/issues/{iid}/notes"
        data = await self.client.get(path)
        return [GitLabNote(**n) for n in data]

    async def create_issue_note(
        self,
        iid: int,
        body: str,
        project_id: int | str | None = None,
    ) -> GitLabNote:
        """Create issue note."""
        path = f"{self._project_path(project_id)}/issues/{iid}/notes"
        data = await self.client.post(path, json={"body": body})
        return GitLabNote(**data)
