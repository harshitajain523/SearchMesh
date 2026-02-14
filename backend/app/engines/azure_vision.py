"""
Azure Computer Vision Engine Adapter

Uses Azure Cognitive Services Computer Vision API for image analysis.
Enhances search results with image metadata (tags, descriptions, dimensions).

API Docs: https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/
"""
import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import logging

from app.engines.base import BaseSearchEngine
from app.models.search import SearchResult, SearchSource
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureVisionEngine(BaseSearchEngine):
    """
    Azure Computer Vision adapter.
    
    Uses Azure CV to analyze images found in search results,
    enriching them with tags, captions, and metadata.
    Can also perform visual search by analyzing image content.
    """
    
    @property
    def source(self) -> SearchSource:
        return SearchSource.AZURE_VISION
    
    @property
    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.azure_vision_key and settings.azure_vision_endpoint)
    
    async def _execute_search(
        self,
        query: str,
        max_results: int = 10,
        image_search: bool = False
    ) -> List[SearchResult]:
        """
        Azure Vision doesn't do traditional search.
        Instead it augments image results with AI analysis.
        Returns empty for non-image searches.
        """
        if not image_search:
            return []
        
        # For image search, we return analyzed results
        # In practice, this would work alongside other engines
        return []
    
    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze an image using Azure Computer Vision.
        
        Returns tags, description, dimensions, and other metadata.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict with analysis results
        """
        settings = get_settings()
        
        if not self.is_configured:
            logger.warning("Azure Vision not configured")
            return {}
        
        endpoint = settings.azure_vision_endpoint.rstrip('/')
        url = f"{endpoint}/computervision/imageanalysis:analyze"
        
        headers = {
            "Ocp-Apim-Subscription-Key": settings.azure_vision_key,
            "Content-Type": "application/json",
        }
        
        params = {
            "api-version": "2024-02-01",
            "features": "tags,caption,read,smartCrops",
            "language": "en",
        }
        
        body = {
            "url": image_url
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    url, 
                    headers=headers, 
                    params=params,
                    json=body
                )
                response.raise_for_status()
                data = response.json()
            
            await self.circuit_breaker.record_success()
            return self._parse_analysis(data)
            
        except Exception as e:
            await self.circuit_breaker.record_failure()
            logger.error(f"Azure Vision analysis failed: {e}")
            return {}
    
    async def analyze_image_batch(
        self, 
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """
        Enrich search results with Azure Vision analysis.
        
        Analyzes images in results and adds tags, captions, etc.
        
        Args:
            results: List of search results with image_url
            
        Returns:
            Enriched search results
        """
        if not self.is_configured:
            return results
        
        enriched = []
        for result in results:
            if result.image_url:
                analysis = await self.analyze_image(result.image_url)
                if analysis:
                    # Add Azure Vision tags to snippet
                    tags = analysis.get("tags", [])
                    caption = analysis.get("caption", "")
                    
                    if caption and not result.snippet:
                        result.snippet = caption
                    
                    if tags:
                        tag_text = ", ".join(tags[:5])
                        result.snippet += f" [Tags: {tag_text}]"
                    
                    # Update dimensions
                    if analysis.get("width") and not result.width:
                        result.width = analysis["width"]
                    if analysis.get("height") and not result.height:
                        result.height = analysis["height"]
            
            enriched.append(result)
        
        return enriched
    
    def _parse_analysis(self, data: dict) -> Dict[str, Any]:
        """Parse Azure Vision API response."""
        result = {}
        
        # Caption
        caption_result = data.get("captionResult", {})
        if caption_result:
            result["caption"] = caption_result.get("text", "")
            result["caption_confidence"] = caption_result.get("confidence", 0)
        
        # Tags
        tags_result = data.get("tagsResult", {})
        if tags_result:
            result["tags"] = [
                tag["name"] 
                for tag in tags_result.get("values", [])
                if tag.get("confidence", 0) > 0.5
            ]
        
        # Metadata (dimensions)
        metadata = data.get("metadata", {})
        if metadata:
            result["width"] = metadata.get("width")
            result["height"] = metadata.get("height")
        
        # Read results (OCR text in image)
        read_result = data.get("readResult", {})
        if read_result:
            blocks = read_result.get("blocks", [])
            text_lines = []
            for block in blocks:
                for line in block.get("lines", []):
                    text_lines.append(line.get("text", ""))
            if text_lines:
                result["ocr_text"] = " ".join(text_lines)
        
        return result
