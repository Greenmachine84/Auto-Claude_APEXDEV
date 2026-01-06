"""
APEX Development Platform - JIRA Client
Phase 4: UI, Integrations & Analytics

HTTP client for JIRA API interactions.
"""

import base64
import logging
from typing import Any, Optional

import httpx

from .models import JiraConfig

logger = logging.getLogger(__name__)


class JiraClientError(Exception):
    """JIRA client error."""

    def __init__(self, message: str, status_code: Optional[int] = None, errors: Optional[list] = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors or []


class JiraClient:
    """JIRA REST API HTTP client."""

    def __init__(self, config: JiraConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/") + "/rest/api/3"
        self.agile_url = config.base_url.rstrip("/") + "/rest/agile/1.0"
        self._client: Optional[httpx.AsyncClient] = None

    def _get_auth_header(self) -> str:
        """Get Basic auth header."""
        credentials = f"{self.config.email}:{self.config.api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": self._get_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
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
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> Any:
        """Make API request."""
        client = await self._get_client()
        try:
            response = await client.request(method, url, params=params, json=json)
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
            message = str(e)
            errors = []
            if error_data:
                errors = error_data.get("errorMessages", [])
                if errors:
                    message = "; ".join(errors)
                elif "errors" in error_data:
                    message = str(error_data["errors"])
            logger.error(f"JIRA API error: {message} (status={e.response.status_code})")
            raise JiraClientError(message, e.response.status_code, errors) from e
        except httpx.RequestError as e:
            logger.error(f"JIRA API request failed: {e}")
            raise JiraClientError(str(e)) from e

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        """GET request."""
        return await self._request("GET", f"{self.base_url}{path}", params=params)

    async def post(self, path: str, json: Optional[dict] = None) -> Any:
        """POST request."""
        return await self._request("POST", f"{self.base_url}{path}", json=json)

    async def put(self, path: str, json: Optional[dict] = None) -> Any:
        """PUT request."""
        return await self._request("PUT", f"{self.base_url}{path}", json=json)

    async def delete(self, path: str) -> Any:
        """DELETE request."""
        return await self._request("DELETE", f"{self.base_url}{path}")

    async def get_agile(self, path: str, params: Optional[dict] = None) -> Any:
        """GET request to Agile API."""
        return await self._request("GET", f"{self.agile_url}{path}", params=params)

    async def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Search issues using JQL."""
        payload = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
        }
        if fields:
            payload["fields"] = fields
        return await self._request("POST", f"{self.base_url}/search", json=payload)
