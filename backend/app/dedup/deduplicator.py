"""
Deduplication Engine

Combines multiple deduplication strategies to identify and remove duplicates.
"""
from typing import List, Dict, Set, Optional
import logging

from app.models.search import SearchResult
from app.dedup.url_normalizer import URLNormalizer, url_normalizer
from app.dedup.fuzzy_matcher import FuzzyMatcher, fuzzy_matcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Multi-strategy deduplication engine.
    
    Strategies:
    1. URL normalization: Exact URL match after normalization
    2. Fuzzy title matching: Content similarity using Jaccard
    3. Domain + title: Same domain with similar title
    
    Results are scored to keep the best version of each duplicate group.
    """
    
    def __init__(
        self,
        url_normalizer: URLNormalizer = url_normalizer,
        fuzzy_matcher: FuzzyMatcher = fuzzy_matcher,
        enable_fuzzy: bool = True
    ):
        """
        Initialize deduplicator.
        
        Args:
            url_normalizer: URL normalizer instance
            fuzzy_matcher: Fuzzy matcher instance
            enable_fuzzy: Whether to use fuzzy title matching
        """
        self.url_normalizer = url_normalizer
        self.fuzzy_matcher = fuzzy_matcher
        self.enable_fuzzy = enable_fuzzy
    
    def deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove duplicates from search results.
        
        Args:
            results: List of search results
            
        Returns:
            Deduplicated list with best version of each result
        """
        if not results:
            return []
        
        # Phase 1: Normalize URLs and mark exact duplicates
        results = self._normalize_urls(results)
        
        # Phase 2: Group by normalized URL
        url_groups = self._group_by_url(results)
        
        # Phase 3: Merge groups (keep best from each group)
        unique_results = self._merge_url_groups(url_groups)
        
        # Phase 4: Fuzzy title matching (if enabled)
        if self.enable_fuzzy:
            unique_results = self._fuzzy_deduplicate(unique_results)
        
        logger.info(
            f"Deduplication: {len(results)} → {len(unique_results)} "
            f"(removed {len(results) - len(unique_results)})"
        )
        
        return unique_results
    
    def _normalize_urls(self, results: List[SearchResult]) -> List[SearchResult]:
        """Normalize URLs in all results."""
        for result in results:
            result.normalized_url = self.url_normalizer.normalize(result.url)
        return results
    
    def _group_by_url(self, results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """Group results by normalized URL."""
        groups: Dict[str, List[SearchResult]] = {}
        
        for result in results:
            key = result.normalized_url or result.url
            if key not in groups:
                groups[key] = []
            groups[key].append(result)
        
        return groups
    
    def _merge_url_groups(self, groups: Dict[str, List[SearchResult]]) -> List[SearchResult]:
        """Merge each group, keeping the best result."""
        merged = []
        
        for url, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Mark duplicates and keep best
                best = self._select_best(group)
                
                # Mark others as duplicates
                for result in group:
                    if result != best:
                        result.is_duplicate = True
                        result.duplicate_of = best.url
                
                merged.append(best)
        
        return merged
    
    def _select_best(self, group: List[SearchResult]) -> SearchResult:
        """
        Select the best result from a duplicate group.
        
        Scoring factors:
        - Source weight (Google > Bing > DDG for web)
        - Metadata completeness
        - Snippet length
        """
        def score(result: SearchResult) -> float:
            s = 0.0
            
            # Source weight
            source_weights = {
                'google': 1.2,
                'bing': 1.0,
                'duckduckgo': 0.9,
            }
            s += source_weights.get(result.source, 1.0)
            
            # Metadata completeness
            if result.thumbnail_url:
                s += 0.2
            if result.snippet and len(result.snippet) > 100:
                s += 0.3
            
            # Higher position is better (lower number)
            if result.position:
                s += max(0, (20 - result.position) / 20)
            
            return s
        
        return max(group, key=score)
    
    def _fuzzy_deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove fuzzy title duplicates.
        
        Compares titles between results with different URLs.
        """
        if len(results) < 2:
            return results
        
        unique: List[SearchResult] = []
        seen_titles: List[str] = []
        
        for result in results:
            is_duplicate = False
            
            for seen_title in seen_titles:
                if self.fuzzy_matcher.are_similar(result.title, seen_title):
                    is_duplicate = True
                    result.is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(result)
                seen_titles.append(result.title)
        
        return unique


# Global deduplicator instance
deduplicator = Deduplicator()
