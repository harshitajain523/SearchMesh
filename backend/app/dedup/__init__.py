"""Deduplication module exports."""
from app.dedup.url_normalizer import URLNormalizer, url_normalizer
from app.dedup.fuzzy_matcher import FuzzyMatcher, fuzzy_matcher
from app.dedup.deduplicator import Deduplicator, deduplicator

__all__ = [
    "URLNormalizer",
    "url_normalizer",
    "FuzzyMatcher", 
    "fuzzy_matcher",
    "Deduplicator",
    "deduplicator",
]
