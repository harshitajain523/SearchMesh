"""
DuckDuckGo Search Engine Adapter

Uses DuckDuckGo Instant Answer API and HTML scraping.
Note: DuckDuckGo doesn't have an official API, so we use ddg_search library
or fallback to HTML scraping.
"""
import httpx
from typing import List
from urllib.parse import urlparse, quote_plus
import logging
import re

from app.engines.base import BaseSearchEngine
from app.models.search import SearchResult, SearchSource
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# DuckDuckGo HTML search URL
DDG_HTML_URL = "https://html.duckduckgo.com/html/"


class DuckDuckGoSearchEngine(BaseSearchEngine):
    """DuckDuckGo search adapter using HTML scraping."""
    
    @property
    def source(self) -> SearchSource:
        return SearchSource.DUCKDUCKGO
    
    @property
    def is_configured(self) -> bool:
        # DuckDuckGo doesn't require API keys
        return True
    
    async def _execute_search(
        self, 
        query: str, 
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """Execute DuckDuckGo search via HTML scraping."""
        settings = get_settings()
        
        if image_search:
            # Image search requires different approach
            return await self._search_images(query, max_results)
        
        return await self._search_web(query, max_results)
    
    async def _search_web(self, query: str, max_results: int) -> List[SearchResult]:
        """Search web results via HTML scraping."""
        settings = get_settings()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        data = {
            "q": query,
            "b": "",
        }
        
        async with httpx.AsyncClient(timeout=settings.search_timeout) as client:
            response = await client.post(DDG_HTML_URL, headers=headers, data=data)
            response.raise_for_status()
            html = response.text
        
        return self._parse_html_results(html, max_results)
    
    def _parse_html_results(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse DuckDuckGo HTML response."""
        results = []
        
        # Simple regex parsing for result links
        # Pattern matches result divs with class="result"
        result_pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
        snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]*(?:<[^>]+>[^<]*)*)</a>'
        
        links = re.findall(result_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        for i, (url, title) in enumerate(links[:max_results]):
            # Clean title
            title = self._clean_html(title)
            
            # Get snippet if available
            snippet = ""
            if i < len(snippets):
                snippet = self._clean_html(snippets[i])
            
            # Parse domain
            domain = urlparse(url).netloc if url else None
            
            results.append(SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                source=self.source,
                domain=domain,
            ))
        
        return results
    
    async def _search_images(self, query: str, max_results: int) -> List[SearchResult]:
        """Search images - simplified implementation."""
        # For images, we'd need to use a different approach
        # For now, return empty list and log
        logger.info("DuckDuckGo image search not fully implemented")
        return []
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text."""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        clean = clean.replace('&quot;', '"')
        clean = clean.replace('&#x27;', "'")
        clean = clean.replace('&nbsp;', ' ')
        # Clean whitespace
        clean = ' '.join(clean.split())
        return clean.strip()
