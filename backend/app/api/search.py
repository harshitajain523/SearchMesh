"""
Search API Routes

REST endpoints for search functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from app.models.search import (
    SearchRequest,
    SearchSource,
    AggregatedResults,
    SourceStatus,
)
from app.engines.aggregator import aggregator
from app.dedup.deduplicator import deduplicator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=AggregatedResults)
async def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    sources: Optional[List[SearchSource]] = Query(
        default=None,
        description="Search engines to query (default: all)"
    ),
    max_results: int = Query(default=30, ge=1, le=100, description="Maximum results"),
    image_search: bool = Query(default=False, description="Search for images"),
    dedupe: bool = Query(default=True, description="Enable deduplication"),
) -> AggregatedResults:
    """
    Execute federated search across multiple engines.
    
    - **q**: Search query string
    - **sources**: List of search engines (google, bing, duckduckgo)
    - **max_results**: Maximum number of results to return
    - **image_search**: Whether to search for images
    - **dedupe**: Whether to deduplicate results
    
    Returns aggregated, deduplicated results from all sources.
    """
    # Build request
    request = SearchRequest(
        query=q,
        sources=sources or [SearchSource.GOOGLE, SearchSource.BING, SearchSource.DUCKDUCKGO],
        max_results=max_results,
        image_search=image_search,
    )
    
    # Execute search
    dedup = deduplicator if dedupe else None
    results = await aggregator.search(request, deduplicator=dedup)
    
    logger.info(
        f"Search: '{q}' - {results.total_results} results, "
        f"{results.duplicates_removed} duplicates removed, "
        f"{results.processing_time_ms:.0f}ms"
    )
    
    return results


@router.post("", response_model=AggregatedResults)
async def search_post(request: SearchRequest) -> AggregatedResults:
    """
    Execute federated search with full request body.
    
    Use this endpoint for complex searches with filters.
    """
    results = await aggregator.search(request, deduplicator=deduplicator)
    return results


@router.get("/engines", response_model=List[dict])
async def get_engine_status() -> List[dict]:
    """
    Get status of all search engines.
    
    Returns configuration and circuit breaker status for each engine.
    """
    return aggregator.get_engine_status()
