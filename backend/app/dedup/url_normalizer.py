"""
URL Normalizer

Normalizes URLs to enable duplicate detection across different sources.
"""
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional
import re


# Tracking parameters to remove
TRACKING_PARAMS = {
    # UTM parameters
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    # Facebook
    'fbclid', 'fb_action_ids', 'fb_action_types', 'fb_source', 'fb_ref',
    # Google
    'gclid', 'gclsrc', 'dclid',
    # Microsoft
    'msclkid',
    # Twitter
    'twclid',
    # Generic
    'ref', 'ref_src', 'ref_url', 'source', 'campaign',
    # Session/tracking
    'sessionid', 'session_id', 'sid', 'visitor_id',
    # Analytics
    '_ga', '_gl', '_hsenc', '_hsmi', 'mc_cid', 'mc_eid',
    # Others
    'affiliate', 'partner', 'referrer',
}


class URLNormalizer:
    """
    Normalizes URLs to detect duplicates.
    
    Operations:
    1. Remove tracking parameters (utm_*, fbclid, etc.)
    2. Normalize protocol (http → https)
    3. Remove www subdomain
    4. Sort query parameters
    5. Convert to lowercase
    6. Remove trailing slashes
    7. Remove default ports
    8. Remove fragment (hash)
    """
    
    def normalize(self, url: str) -> str:
        """
        Normalize a URL for comparison.
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL string
        """
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            
            # Normalize scheme (prefer https)
            scheme = 'https' if parsed.scheme in ('http', 'https') else parsed.scheme
            
            # Normalize host (lowercase, remove www)
            host = parsed.netloc.lower()
            host = self._remove_default_port(host, scheme)
            host = self._remove_www(host)
            
            # Normalize path (lowercase, remove trailing slash)
            path = parsed.path.lower()
            path = self._normalize_path(path)
            
            # Filter and sort query parameters
            query = self._normalize_query(parsed.query)
            
            # Reconstruct URL (without fragment)
            normalized = urlunparse((
                scheme,
                host,
                path,
                '',  # params
                query,
                ''   # fragment
            ))
            
            return normalized
            
        except Exception:
            # Return original if parsing fails
            return url.lower().strip()
    
    def _remove_www(self, host: str) -> str:
        """Remove www. prefix from hostname."""
        if host.startswith('www.'):
            return host[4:]
        return host
    
    def _remove_default_port(self, host: str, scheme: str) -> str:
        """Remove default ports (80 for http, 443 for https)."""
        if scheme == 'https' and host.endswith(':443'):
            return host[:-4]
        if scheme == 'http' and host.endswith(':80'):
            return host[:-3]
        return host
    
    def _normalize_path(self, path: str) -> str:
        """Normalize URL path."""
        # Remove trailing slash (except for root)
        if path != '/' and path.endswith('/'):
            path = path[:-1]
        
        # Remove index files
        for index in ['/index.html', '/index.php', '/index.htm', '/default.aspx']:
            if path.endswith(index):
                path = path[:-len(index)] or '/'
        
        # Normalize multiple slashes
        path = re.sub(r'/+', '/', path)
        
        return path or '/'
    
    def _normalize_query(self, query: str) -> str:
        """Filter tracking params and sort remaining."""
        if not query:
            return ''
        
        params = parse_qs(query, keep_blank_values=True)
        
        # Filter out tracking parameters
        filtered = {
            k: v for k, v in params.items()
            if k.lower() not in TRACKING_PARAMS
        }
        
        if not filtered:
            return ''
        
        # Sort parameters for consistent comparison
        sorted_params = sorted(filtered.items())
        
        # Rebuild query string
        return urlencode(sorted_params, doseq=True)
    
    def extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            return self._remove_www(host)
        except Exception:
            return None
    
    def are_same_url(self, url1: str, url2: str) -> bool:
        """Check if two URLs are the same after normalization."""
        return self.normalize(url1) == self.normalize(url2)


# Global normalizer instance
url_normalizer = URLNormalizer()
