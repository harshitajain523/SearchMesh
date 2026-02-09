"""
Bing Web Search Engine Adapter

Uses Bing Web Search API v7.
API Docs: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/
"""
import httpx
from typing import List
from urllib.parse import urlparse
import logging

from app.engines.base import BaseSearchEngine
from app.models.search import SearchResult, SearchSource
from app.core.config import get_settings

logger = logging.getLogger(__name__)

BING_WEB_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
BING_IMAGE_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/images/search"


class BingSearchEngine(BaseSearchEngine):
    """Bing Web Search API adapter."""
    
    @property
    def source(self) -> SearchSource:
        return SearchSource.BING
    
    @property
    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.bing_api_key)
    
    async def _execute_search(
        self, 
        query: str, 
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """Execute Bing Search API call."""
        settings = get_settings()
        
        url = BING_IMAGE_SEARCH_URL if image_search else BING_WEB_SEARCH_URL
        
        headers = {
            "Ocp-Apim-Subscription-Key": settings.bing_api_key,
        }
        
        params = {
            "q": query,
            "count": min(max_results, 50),  # Bing API max is 50
            "mkt": "en-US",
        }
        
        if image_search:
            params["imageType"] = "Photo"
        
        async with httpx.AsyncClient(timeout=settings.search_timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        
        return self._parse_results(data, image_search)
    
    def _parse_results(self, data: dict, image_search: bool) -> List[SearchResult]:
        """Parse Bing API response to SearchResult objects."""
        results = []
        
        if image_search:
            items = data.get("value", [])
        else:
            items = data.get("webPages", {}).get("value", [])
        
        for item in items:
            try:
                if image_search:
                    result = self._parse_image_result(item)
                else:
                    result = self._parse_web_result(item)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse result: {e}")
                continue
        
        return results
    
    def _parse_web_result(self, item: dict) -> SearchResult:
        """Parse a web search result."""
        url = item.get("url", "")
        domain = urlparse(url).netloc if url else None
        
        return SearchResult(
            title=item.get("name", ""),
            url=url,
            snippet=item.get("snippet", ""),
            source=self.source,
            domain=domain,
        )
    
    def _parse_image_result(self, item: dict) -> SearchResult:
        """Parse an image search result."""
        content_url = item.get("contentUrl", "")
        domain = urlparse(content_url).netloc if content_url else None
        
        return SearchResult(
            title=item.get("name", ""),
            url=item.get("hostPageUrl", content_url),
            snippet=item.get("name", ""),
            source=self.source,
            domain=domain,
            image_url=content_url,
            thumbnail_url=item.get("thumbnailUrl"),
            width=item.get("width"),
            height=item.get("height"),
            file_size=item.get("contentSize"),
        )
