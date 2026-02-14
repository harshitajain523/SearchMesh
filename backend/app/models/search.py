"""
Pydantic models for search results and requests.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SearchSource(str, Enum):
    """Search engine sources."""
    GOOGLE = "google"
    DUCKDUCKGO = "duckduckgo"
    AZURE_VISION = "azure_vision"


class SearchResult(BaseModel):
    """Individual search result from any source."""
    title: str
    url: str
    snippet: str
    source: SearchSource
    position: int = 0
    
    # Optional metadata
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    domain: Optional[str] = None
    
    # Scoring
    relevance_score: float = 1.0
    source_weight: float = 1.0
    final_score: float = 0.0
    
    # Deduplication
    normalized_url: Optional[str] = None
    content_hash: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    
    # Timestamps
    fetched_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class SearchRequest(BaseModel):
    """Search request from client."""
    query: str = Field(..., min_length=1, max_length=500)
    sources: List[SearchSource] = Field(
        default=[SearchSource.GOOGLE, SearchSource.DUCKDUCKGO]
    )
    max_results: int = Field(default=30, ge=1, le=100)
    
    # Filters
    image_search: bool = False
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    exclude_domains: List[str] = Field(default_factory=list)
    include_domains: List[str] = Field(default_factory=list)
    
    # Profile
    profile_id: Optional[str] = None


class AggregatedResults(BaseModel):
    """Aggregated search results from all sources."""
    query: str
    results: List[SearchResult]
    total_results: int
    sources_queried: List[SearchSource]
    sources_succeeded: List[SearchSource]
    sources_failed: List[SearchSource]
    
    # Stats
    duplicates_removed: int = 0
    processing_time_ms: float = 0
    cache_hit: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)


class SourceStatus(BaseModel):
    """Status of a search source."""
    source: SearchSource
    available: bool
    circuit_state: str
    last_error: Optional[str] = None
    response_time_ms: Optional[float] = None


class SystemHealth(BaseModel):
    """System health status."""
    status: str
    sources: List[SourceStatus]
    cache_available: bool
    database_available: bool
