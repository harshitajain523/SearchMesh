"""
Fuzzy Title Matcher

Uses Jaccard similarity on tokenized titles to detect duplicate content.
"""
import re
from typing import Set, Tuple
import logging

logger = logging.getLogger(__name__)


# Stop words to remove from titles
STOP_WORDS = {
    # English articles and prepositions
    'a', 'an', 'the', 'and', 'or', 'but', 'for', 'nor', 'so', 'yet',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'it',
    # Common filler words
    'best', 'top', 'new', 'free', 'how', 'what', 'why', 'when', 'where',
    'your', 'our', 'with', 'from', 'this', 'that', 'these', 'those',
    # Years (common in titles)
    '2024', '2025', '2026',
    # Common marketing words
    'official', 'ultimate', 'complete', 'guide', 'review', 'reviews',
}


class FuzzyMatcher:
    """
    Fuzzy title matching using Jaccard similarity.
    
    Algorithm:
    1. Tokenize title into words
    2. Remove stop words and normalize
    3. Compute Jaccard similarity: |intersection| / |union|
    4. If similarity > threshold, mark as duplicates
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize fuzzy matcher.
        
        Args:
            similarity_threshold: Minimum Jaccard similarity to consider duplicates
        """
        self.similarity_threshold = similarity_threshold
    
    def tokenize(self, text: str) -> Set[str]:
        """
        Tokenize text into normalized word set.
        
        Args:
            text: Input text
            
        Returns:
            Set of normalized tokens
        """
        if not text:
            return set()
        
        # Lowercase
        text = text.lower()
        
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Remove stop words and short words
        tokens = {
            word for word in words 
            if word not in STOP_WORDS and len(word) > 2
        }
        
        return tokens
    
    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """
        Compute Jaccard similarity between two sets.
        
        Jaccard = |intersection| / |union|
        
        Args:
            set1: First set of tokens
            set2: Second set of tokens
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def compare(self, title1: str, title2: str) -> Tuple[float, bool]:
        """
        Compare two titles for similarity.
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            Tuple of (similarity_score, is_duplicate)
        """
        tokens1 = self.tokenize(title1)
        tokens2 = self.tokenize(title2)
        
        similarity = self.jaccard_similarity(tokens1, tokens2)
        is_duplicate = similarity >= self.similarity_threshold
        
        return similarity, is_duplicate
    
    def are_similar(self, title1: str, title2: str) -> bool:
        """
        Check if two titles are similar enough to be duplicates.
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            True if titles are similar
        """
        _, is_duplicate = self.compare(title1, title2)
        return is_duplicate


# Global matcher instance
fuzzy_matcher = FuzzyMatcher(similarity_threshold=0.7)
