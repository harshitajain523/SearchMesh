"""
Base Search Engine Interface

Abstract base class defining the contract for all search engine adapters.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging

from app.models.search import SearchResult, SearchSource
from app.core.circuit_breaker import CircuitBreaker, circuit_registry

logger = logging.getLogger(__name__)


class BaseSearchEngine(ABC):
    """
    Abstract base class for search engine adapters.
    
    Each search engine implementation must provide:
    - source: The SearchSource enum value
    - search(): Main search method
    - _parse_results(): Parse API response to SearchResult objects
    """
    
    def __init__(self):
        self.circuit_breaker = circuit_registry.get_or_create(
            name=self.source.value,
            failure_threshold=5,
            timeout_duration=30
        )
    
    @property
    @abstractmethod
    def source(self) -> SearchSource:
        """Return the source identifier for this engine."""
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the engine has required API keys configured."""
        pass
    
    @abstractmethod
    async def _execute_search(
        self, 
        query: str, 
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """
        Execute the actual search API call.
        
        This method should:
        1. Make the API request
        2. Parse the response
        3. Return list of SearchResult objects
        
        Raises:
            Exception: On API errors
        """
        pass
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """
        Search with circuit breaker protection.
        
        Args:
            query: Search query string
            max_results: Maximum results to return
            image_search: Whether to search for images
            
        Returns:
            List of SearchResult objects
        """
        if not self.is_configured:
            logger.warning(f"{self.source.value}: Not configured, skipping")
            return []
        
        # Check circuit breaker
        if not await self.circuit_breaker.try_acquire():
            logger.warning(f"{self.source.value}: Circuit breaker open, skipping")
            return []
        
        try:
            results = await self._execute_search(
                query=query,
                max_results=max_results,
                image_search=image_search
            )
            
            # Record success
            await self.circuit_breaker.record_success()
            
            # Add position and source info
            for i, result in enumerate(results):
                result.position = i + 1
                result.source = self.source
            
            logger.info(f"{self.source.value}: Found {len(results)} results")
            return results
            
        except Exception as e:
            await self.circuit_breaker.record_failure()
            logger.error(f"{self.source.value}: Search failed - {e}")
            raise
    
    def get_status(self) -> dict:
        """Get engine status including circuit breaker state."""
        return {
            "source": self.source.value,
            "configured": self.is_configured,
            "circuit_breaker": self.circuit_breaker.get_stats()
        }
