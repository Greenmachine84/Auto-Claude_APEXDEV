"""
APEX Development Platform - GitHub Service
Phase 4: UI, Integrations & Analytics

High-level service for GitHub operations.
"""

import logging
from typing import Optional

from .client import GitHubClient
from .models import (
    GitHubConfig,
    GitHubComment,
    GitHubIssue,
    GitHubPullRequest,
    GitHubRepository,
    GitHubReview,
    GitHubUser,
    IssueState,
    PullRequestState,
    ReviewState,
)

logger = logging.getLogger(__name__)


class GitHubService:
    """High-level GitHub service."""

    def __init__(self, config: GitHubConfig):
        self.config = config
        self.client = GitHubClient(config)
        self._owner = config.default_owner
        self._repo = config.default_repo

    def _repo_path(self, owner: Optional[str] = None, repo: Optional[str] = None) -> str:
        """Build repository path."""
        o = owner or self._owner
        r = repo or self._repo
        if not o or not r:
            raise ValueError("Owner and repo must be specified")
        return f"/repos/{o}/{r}"

    async def close(self) -> None:
        """Close service."""
        await self.client.close()

    # User methods
    async def get_authenticated_user(self) -> GitHubUser:
        """Get authenticated user."""
        data = await self.client.get("/user")
        return GitHubUser(**data)

    # Repository methods
    async def get_repository(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubRepository:
        """Get repository details."""
        path = self._repo_path(owner, repo)
        data = await self.client.get(path)
        return GitHubRepository(**data)

    async def list_repositories(self, org: Optional[str] = None) -> list[GitHubRepository]:
        """List repositories."""
        if org:
            data = await self.client.paginate(f"/orgs/{org}/repos")
        else:
            data = await self.client.paginate("/user/repos")
        return [GitHubRepository(**r) for r in data]

    # Pull request methods
    async def list_pull_requests(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        state: PullRequestState = PullRequestState.OPEN,
    ) -> list[GitHubPullRequest]:
        """List pull requests."""
        path = f"{self._repo_path(owner, repo)}/pulls"
        data = await self.client.paginate(path, {"state": state.value})
        return [GitHubPullRequest(**pr) for pr in data]

    async def get_pull_request(
        self,
        number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubPullRequest:
        """Get pull request details."""
        path = f"{self._repo_path(owner, repo)}/pulls/{number}"
        data = await self.client.get(path)
        return GitHubPullRequest(**data)

    async def create_pull_request(
        self,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubPullRequest:
        """Create pull request."""
        path = f"{self._repo_path(owner, repo)}/pulls"
        data = await self.client.post(
            path,
            json={"title": title, "head": head, "base": base, "body": body, "draft": draft},
        )
        return GitHubPullRequest(**data)

    async def update_pull_request(
        self,
        number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[PullRequestState] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubPullRequest:
        """Update pull request."""
        path = f"{self._repo_path(owner, repo)}/pulls/{number}"
        payload = {}
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if state:
            payload["state"] = state.value
        data = await self.client.patch(path, json=payload)
        return GitHubPullRequest(**data)

    async def merge_pull_request(
        self,
        number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge",
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> dict:
        """Merge pull request."""
        path = f"{self._repo_path(owner, repo)}/pulls/{number}/merge"
        payload = {"merge_method": merge_method}
        if commit_title:
            payload["commit_title"] = commit_title
        if commit_message:
            payload["commit_message"] = commit_message
        return await self.client.put(path, json=payload)

    # Review methods
    async def list_reviews(
        self,
        pr_number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> list[GitHubReview]:
        """List pull request reviews."""
        path = f"{self._repo_path(owner, repo)}/pulls/{pr_number}/reviews"
        data = await self.client.get(path)
        return [GitHubReview(**r) for r in data]

    async def create_review(
        self,
        pr_number: int,
        body: Optional[str] = None,
        event: ReviewState = ReviewState.COMMENTED,
        comments: Optional[list[dict]] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubReview:
        """Create pull request review."""
        path = f"{self._repo_path(owner, repo)}/pulls/{pr_number}/reviews"
        payload = {"event": event.value}
        if body:
            payload["body"] = body
        if comments:
            payload["comments"] = comments
        data = await self.client.post(path, json=payload)
        return GitHubReview(**data)

    # Issue methods
    async def list_issues(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        state: IssueState = IssueState.OPEN,
        labels: Optional[list[str]] = None,
    ) -> list[GitHubIssue]:
        """List issues."""
        path = f"{self._repo_path(owner, repo)}/issues"
        params = {"state": state.value}
        if labels:
            params["labels"] = ",".join(labels)
        data = await self.client.paginate(path, params)
        # Filter out pull requests (they appear in issues endpoint)
        return [GitHubIssue(**i) for i in data if "pull_request" not in i]

    async def get_issue(
        self,
        number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubIssue:
        """Get issue details."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}"
        data = await self.client.get(path)
        return GitHubIssue(**data)

    async def create_issue(
        self,
        title: str,
        body: Optional[str] = None,
        labels: Optional[list[str]] = None,
        assignees: Optional[list[str]] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubIssue:
        """Create issue."""
        path = f"{self._repo_path(owner, repo)}/issues"
        payload = {"title": title}
        if body:
            payload["body"] = body
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        data = await self.client.post(path, json=payload)
        return GitHubIssue(**data)

    async def update_issue(
        self,
        number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[IssueState] = None,
        labels: Optional[list[str]] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubIssue:
        """Update issue."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}"
        payload = {}
        if title:
            payload["title"] = title
        if body:
            payload["body"] = body
        if state:
            payload["state"] = state.value
        if labels is not None:
            payload["labels"] = labels
        data = await self.client.patch(path, json=payload)
        return GitHubIssue(**data)

    # Comment methods
    async def list_issue_comments(
        self,
        number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> list[GitHubComment]:
        """List issue comments."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}/comments"
        data = await self.client.get(path)
        return [GitHubComment(**c) for c in data]

    async def create_issue_comment(
        self,
        number: int,
        body: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> GitHubComment:
        """Create issue comment."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}/comments"
        data = await self.client.post(path, json={"body": body})
        return GitHubComment(**data)
