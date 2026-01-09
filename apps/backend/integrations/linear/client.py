"""
APEX Development Platform - Linear Client
Phase 4: UI, Integrations & Analytics

GraphQL client for Linear API interactions.
"""

import logging
from typing import Any

import httpx

from .models import LinearConfig

logger = logging.getLogger(__name__)


class LinearClientError(Exception):
    """Linear client error."""

    def __init__(self, message: str, errors: list | None = None):
        super().__init__(message)
        self.errors = errors or []


class LinearClient:
    """Linear GraphQL API client."""

    def __init__(self, config: LinearConfig):
        self.config = config
        self.base_url = config.base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": self.config.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def query(
        self,
        query: str,
        variables: dict | None = None,
    ) -> dict[str, Any]:
        """Execute GraphQL query."""
        client = await self._get_client()
        try:
            response = await client.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
            )
            response.raise_for_status()
            result = response.json()

            if "errors" in result:
                errors = result["errors"]
                message = (
                    errors[0].get("message", "Unknown error")
                    if errors
                    else "Unknown error"
                )
                logger.error(f"Linear GraphQL error: {message}")
                raise LinearClientError(message, errors)

            return result.get("data", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"Linear API error: {e}")
            raise LinearClientError(str(e)) from e
        except httpx.RequestError as e:
            logger.error(f"Linear API request failed: {e}")
            raise LinearClientError(str(e)) from e

    async def mutate(
        self,
        mutation: str,
        variables: dict | None = None,
    ) -> dict[str, Any]:
        """Execute GraphQL mutation."""
        return await self.query(mutation, variables)

    # Common query fragments
    USER_FRAGMENT = """
        fragment UserFields on User {
            id
            name
            email
            displayName
            avatarUrl
            active
            admin
        }
    """

    LABEL_FRAGMENT = """
        fragment LabelFields on IssueLabel {
            id
            name
            color
            description
        }
    """

    ISSUE_FRAGMENT = """
        fragment IssueFields on Issue {
            id
            identifier
            title
            description
            priority
            priorityLabel
            url
            state { id name type }
            assignee { ...UserFields }
            creator { ...UserFields }
            team { id key name }
            project { id name slugId }
            cycle { id number name }
            labels { nodes { ...LabelFields } }
            estimate
            dueDate
            startedAt
            completedAt
            cancelledAt
            createdAt
            updatedAt
            archivedAt
        }
    """

    PROJECT_FRAGMENT = """
        fragment ProjectFields on Project {
            id
            name
            description
            slugId
            icon
            color
            state
            progress
            targetDate
            startedAt
            completedAt
            cancelledAt
            createdAt
            updatedAt
        }
    """
