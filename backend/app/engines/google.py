"""
Google Custom Search Engine Adapter

Uses Google Custom Search JSON API.
API Docs: https://developers.google.com/custom-search/v1/overview
"""
import httpx
from typing import List
from urllib.parse import urlparse
import logging

from app.engines.base import BaseSearchEngine
from app.models.search import SearchResult, SearchSource
from app.core.config import get_settings

logger = logging.getLogger(__name__)

GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"


class GoogleSearchEngine(BaseSearchEngine):
    """Google Custom Search API adapter."""
    
    @property
    def source(self) -> SearchSource:
        return SearchSource.GOOGLE
    
    @property
    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.google_api_key and settings.google_search_engine_id)
    
    async def _execute_search(
        self, 
        query: str, 
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """Execute Google Custom Search API call."""
        settings = get_settings()
        
        params = {
            "key": settings.google_api_key,
            "cx": settings.google_search_engine_id,
            "q": query,
            "num": min(max_results, 10),  # Google API max is 10 per request
        }
        
        if image_search:
            params["searchType"] = "image"
        
        async with httpx.AsyncClient(timeout=settings.search_timeout) as client:
            response = await client.get(GOOGLE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        return self._parse_results(data, image_search)
    
    def _parse_results(self, data: dict, image_search: bool) -> List[SearchResult]:
        """Parse Google API response to SearchResult objects."""
        results = []
        items = data.get("items", [])
        
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
        url = item.get("link", "")
        domain = urlparse(url).netloc if url else None
        
        return SearchResult(
            title=item.get("title", ""),
            url=url,
            snippet=item.get("snippet", ""),
            source=self.source,
            domain=domain,
            thumbnail_url=item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src"),
        )
    
    def _parse_image_result(self, item: dict) -> SearchResult:
        """Parse an image search result."""
        url = item.get("link", "")
        image = item.get("image", {})
        domain = urlparse(url).netloc if url else None
        
        return SearchResult(
            title=item.get("title", ""),
            url=item.get("image", {}).get("contextLink", url),
            snippet=item.get("snippet", ""),
            source=self.source,
            domain=domain,
            image_url=url,
            thumbnail_url=item.get("image", {}).get("thumbnailLink"),
            width=image.get("width"),
            height=image.get("height"),
            file_size=image.get("byteSize"),
        )
