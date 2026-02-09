"""
SearchMesh Configuration
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "SearchMesh"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    # Search Engine API Keys
    google_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    bing_api_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/searchmesh"
    
    # Cache TTLs (seconds)
    query_cache_ttl: int = 86400  # 24 hours
    api_cache_ttl: int = 21600    # 6 hours
    metadata_cache_ttl: int = 604800  # 7 days
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Circuit Breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 30
    
    # Search
    search_timeout: float = 10.0
    max_results_per_source: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
