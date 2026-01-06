"""Web scrape tool.

Scrapes web pages.

Capabilities:
- Fetch page content
- Extract text
- Parse HTML
- Follow links
"""

from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
import re

from tools.core.base_tool import (
    BaseTool,
    ToolCategory,
    ToolContext,
    ToolResult,
    ToolStatus,
    ToolParameter,
)


class WebScrapeTool(BaseTool):
    """Scrape web pages.
    
    Example:
        tool = WebScrapeTool()
        result = await tool.run(ToolContext(
            tool_call_id="1",
            parameters={
                "url": "https://example.com",
            }
        ))
    """
    
    name = "web_scrape"
    description = "Scrape web pages"
    category = ToolCategory.WEB
    required_permissions = {"http_requests"}
    version = "1.0.0"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get parameter definitions."""
        return [
            ToolParameter(
                name="url",
                type="string",
                description="URL to scrape",
                required=True,
            ),
            ToolParameter(
                name="selector",
                type="string",
                description="CSS selector to extract (simplified)",
                required=False,
                default=None,
            ),
            ToolParameter(
                name="extract_links",
                type="boolean",
                description="Extract all links from page",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="extract_text",
                type="boolean",
                description="Extract text only (strip HTML)",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Timeout in seconds",
                required=False,
                default=30,
            ),
        ]
    
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute web scrape."""
        url = context.parameters.get("url")
        extract_links = context.parameters.get("extract_links", False)
        extract_text = context.parameters.get("extract_text", True)
        timeout = context.parameters.get("timeout", 30)
        
        try:
            # Fetch page
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Bot)"}
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                html = response.read().decode("utf-8", errors="ignore")
            
            result = {
                "url": url,
                "html_length": len(html),
            }
            
            # Extract text
            if extract_text:
                text = self._extract_text(html)
                result["text"] = text
                result["text_length"] = len(text)
            
            # Extract links
            if extract_links:
                links = self._extract_links(html, url)
                result["links"] = links
                result["link_count"] = len(links)
            
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                output=result,
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )
    
    def _extract_text(self, html: str) -> str:
        """Extract text from HTML."""
        # Remove script and style elements
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
    
    def _extract_links(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract links from HTML."""
        links = []
        
        # Find all href attributes
        pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        
        for href, text in matches:
            # Clean text
            text = re.sub(r"<[^>]+>", "", text).strip()
            
            links.append({
                "href": href,
                "text": text[:100],
            })
        
        return links[:100]  # Limit links
