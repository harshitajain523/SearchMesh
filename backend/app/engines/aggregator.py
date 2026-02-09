"""
Search Aggregator

Executes parallel searches across multiple engines and aggregates results.
"""
import asyncio
import time
from typing import List, Optional
import logging

from app.engines.base import BaseSearchEngine
from app.engines.google import GoogleSearchEngine
from app.engines.bing import BingSearchEngine
from app.engines.duckduckgo import DuckDuckGoSearchEngine
from app.models.search import (
    SearchSource, 
    SearchResult, 
    SearchRequest, 
    AggregatedResults
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SearchAggregator:
    """
    Aggregates search results from multiple engines.
    
    Features:
    - Parallel execution using asyncio.gather
    - Graceful error handling (partial results on failures)
    - Timeout handling
    - Circuit breaker integration (via engines)
    """
    
    def __init__(self):
        self.engines: dict[SearchSource, BaseSearchEngine] = {
            SearchSource.GOOGLE: GoogleSearchEngine(),
            SearchSource.BING: BingSearchEngine(),
            SearchSource.DUCKDUCKGO: DuckDuckGoSearchEngine(),
        }
    
    async def search(
        self, 
        request: SearchRequest,
        deduplicator = None,
    ) -> AggregatedResults:
        """
        Execute parallel searches and aggregate results.
        
        Args:
            request: Search request with query and options
            deduplicator: Optional deduplicator to remove duplicates
            
        Returns:
            AggregatedResults with combined results from all sources
        """
        start_time = time.time()
        settings = get_settings()
        
        # Get enabled engines
        engines_to_query = [
            self.engines[source] 
            for source in request.sources 
            if source in self.engines
        ]
        
        # Create search tasks
        tasks = [
            self._search_with_timeout(
                engine=engine,
                query=request.query,
                max_results=request.max_results,
                image_search=request.image_search,
                timeout=settings.search_timeout
            )
            for engine in engines_to_query
        ]
        
        # Execute in parallel
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_results: List[SearchResult] = []
        sources_succeeded: List[SearchSource] = []
        sources_failed: List[SearchSource] = []
        
        for engine, result in zip(engines_to_query, task_results):
            if isinstance(result, Exception):
                logger.error(f"{engine.source.value}: Failed - {result}")
                sources_failed.append(engine.source)
            elif result:
                all_results.extend(result)
                sources_succeeded.append(engine.source)
            else:
                # Empty results (might be unconfigured)
                sources_failed.append(engine.source)
        
        # Apply deduplication if available
        duplicates_removed = 0
        if deduplicator:
            original_count = len(all_results)
            all_results = deduplicator.deduplicate(all_results)
            duplicates_removed = original_count - len(all_results)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        return AggregatedResults(
            query=request.query,
            results=all_results[:request.max_results],
            total_results=len(all_results),
            sources_queried=request.sources,
            sources_succeeded=sources_succeeded,
            sources_failed=sources_failed,
            duplicates_removed=duplicates_removed,
            processing_time_ms=processing_time,
        )
    
    async def _search_with_timeout(
        self,
        engine: BaseSearchEngine,
        query: str,
        max_results: int,
        image_search: bool,
        timeout: float
    ) -> List[SearchResult]:
        """Execute search with timeout."""
        try:
            return await asyncio.wait_for(
                engine.search(
                    query=query,
                    max_results=max_results,
                    image_search=image_search
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"{engine.source.value}: Timeout after {timeout}s")
            raise
    
    def get_engine_status(self) -> List[dict]:
        """Get status of all search engines."""
        return [engine.get_status() for engine in self.engines.values()]


# Global aggregator instance
aggregator = SearchAggregator()
