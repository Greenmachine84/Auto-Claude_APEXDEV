"""
APEX Development Platform - GitHub Service
Phase 4: UI, Integrations & Analytics

High-level service for GitHub operations.
"""

import logging

from .client import GitHubClient
from .models import (
    GitHubComment,
    GitHubConfig,
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

    def _repo_path(
        self, owner: str | None = None, repo: str | None = None
    ) -> str:
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
        owner: str | None = None,
        repo: str | None = None,
    ) -> GitHubRepository:
        """Get repository details."""
        path = self._repo_path(owner, repo)
        data = await self.client.get(path)
        return GitHubRepository(**data)

    async def list_repositories(
        self, org: str | None = None
    ) -> list[GitHubRepository]:
        """List repositories."""
        if org:
            data = await self.client.paginate(f"/orgs/{org}/repos")
        else:
            data = await self.client.paginate("/user/repos")
        return [GitHubRepository(**r) for r in data]

    # Pull request methods
    async def list_pull_requests(
        self,
        owner: str | None = None,
        repo: str | None = None,
        state: PullRequestState = PullRequestState.OPEN,
    ) -> list[GitHubPullRequest]:
        """List pull requests."""
        path = f"{self._repo_path(owner, repo)}/pulls"
        data = await self.client.paginate(path, {"state": state.value})
        return [GitHubPullRequest(**pr) for pr in data]

    async def get_pull_request(
        self,
        number: int,
        owner: str | None = None,
        repo: str | None = None,
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
        body: str | None = None,
        draft: bool = False,
        owner: str | None = None,
        repo: str | None = None,
    ) -> GitHubPullRequest:
        """Create pull request."""
        path = f"{self._repo_path(owner, repo)}/pulls"
        data = await self.client.post(
            path,
            json={
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft,
            },
        )
        return GitHubPullRequest(**data)

    async def update_pull_request(
        self,
        number: int,
        title: str | None = None,
        body: str | None = None,
        state: PullRequestState | None = None,
        owner: str | None = None,
        repo: str | None = None,
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
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        owner: str | None = None,
        repo: str | None = None,
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
        owner: str | None = None,
        repo: str | None = None,
    ) -> list[GitHubReview]:
        """List pull request reviews."""
        path = f"{self._repo_path(owner, repo)}/pulls/{pr_number}/reviews"
        data = await self.client.get(path)
        return [GitHubReview(**r) for r in data]

    async def create_review(
        self,
        pr_number: int,
        body: str | None = None,
        event: ReviewState = ReviewState.COMMENTED,
        comments: list[dict] | None = None,
        owner: str | None = None,
        repo: str | None = None,
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
        owner: str | None = None,
        repo: str | None = None,
        state: IssueState = IssueState.OPEN,
        labels: list[str] | None = None,
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
        owner: str | None = None,
        repo: str | None = None,
    ) -> GitHubIssue:
        """Get issue details."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}"
        data = await self.client.get(path)
        return GitHubIssue(**data)

    async def create_issue(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        owner: str | None = None,
        repo: str | None = None,
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
        title: str | None = None,
        body: str | None = None,
        state: IssueState | None = None,
        labels: list[str] | None = None,
        owner: str | None = None,
        repo: str | None = None,
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
        owner: str | None = None,
        repo: str | None = None,
    ) -> list[GitHubComment]:
        """List issue comments."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}/comments"
        data = await self.client.get(path)
        return [GitHubComment(**c) for c in data]

    async def create_issue_comment(
        self,
        number: int,
        body: str,
        owner: str | None = None,
        repo: str | None = None,
    ) -> GitHubComment:
        """Create issue comment."""
        path = f"{self._repo_path(owner, repo)}/issues/{number}/comments"
        data = await self.client.post(path, json={"body": body})
        return GitHubComment(**data)
