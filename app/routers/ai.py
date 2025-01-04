from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import logging
from ..features.community_insights.implementation import (
    CommunityInsightsRequest,
    CommunityInsightsResponse,
    CommunityInsightsService
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

@router.post("/community-insights", response_model=CommunityInsightsResponse)
async def get_community_insights(
    request: CommunityInsightsRequest
):
    """
    Get community insights using the Perplexity AI model
    Parameters:
    - topic_keyword: Keyword to focus the analysis
    - source_urls: Optional list of URLs to analyze (e.g., Reddit threads, forum discussions)
    - product_urls: Optional list of product URLs to analyze
    - use_only_specified_sources: Whether to only use the specified URLs or allow AI to search additional sources
    """
    try:
        service = CommunityInsightsService()
        return await service.generate_insights(request)
    except Exception as e:
        logger.error(f"Error generating community insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 