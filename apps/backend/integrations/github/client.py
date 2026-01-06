"""
APEX Development Platform - GitHub Client
Phase 4: UI, Integrations & Analytics

HTTP client for GitHub API interactions.
"""

import logging
from typing import Any, Optional

import httpx

from .models import GitHubConfig

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    """GitHub client error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class GitHubClient:
    """GitHub API HTTP client."""

    def __init__(self, config: GitHubConfig):
        self.config = config
        self.base_url = config.enterprise_url or config.base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> Any:
        """Make API request."""
        client = await self._get_client()
        try:
            response = await client.request(method, path, params=params, json=json)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            error_data = None
            try:
                error_data = e.response.json()
            except Exception:
                pass
            message = error_data.get("message", str(e)) if error_data else str(e)
            logger.error(f"GitHub API error: {message} (status={e.response.status_code})")
            raise GitHubClientError(message, e.response.status_code, error_data) from e
        except httpx.RequestError as e:
            logger.error(f"GitHub API request failed: {e}")
            raise GitHubClientError(str(e)) from e

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        """GET request."""
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: Optional[dict] = None) -> Any:
        """POST request."""
        return await self._request("POST", path, json=json)

    async def patch(self, path: str, json: Optional[dict] = None) -> Any:
        """PATCH request."""
        return await self._request("PATCH", path, json=json)

    async def put(self, path: str, json: Optional[dict] = None) -> Any:
        """PUT request."""
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> Any:
        """DELETE request."""
        return await self._request("DELETE", path)

    async def paginate(
        self,
        path: str,
        params: Optional[dict] = None,
        max_pages: int = 10,
    ) -> list[Any]:
        """Paginate through API results."""
        params = params or {}
        params.setdefault("per_page", 100)
        all_items = []
        page = 1

        while page <= max_pages:
            params["page"] = page
            items = await self.get(path, params)
            if not items:
                break
            all_items.extend(items)
            if len(items) < params["per_page"]:
                break
            page += 1

        return all_items
