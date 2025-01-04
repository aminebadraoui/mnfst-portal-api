from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

class CommunityInsightsRequest(BaseModel):
    topic_keyword: str
    source_urls: Optional[List[HttpUrl]] = None
    product_urls: Optional[List[HttpUrl]] = None
    use_only_specified_sources: Optional[bool] = False

class InsightItem(BaseModel):
    title: str
    evidence: str
    source: str
    engagement: str
    frequency: str
    correlation: str
    significance: str
    keyword: str

class InsightSection(BaseModel):
    title: str
    icon: str
    insights: List[InsightItem]

class CommunityInsightsResponse(BaseModel):
    sections: List[InsightSection]

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
        logger.info(f"Received community insights request for topic: {request.topic_keyword}")
        if request.source_urls:
            logger.info(f"Source URLs provided: {request.source_urls}")
        if request.product_urls:
            logger.info(f"Product URLs provided: {request.product_urls}")
        logger.info(f"Use only specified sources: {request.use_only_specified_sources}")

        # For now, return mock data that matches our frontend structure
        mock_response = {
            "sections": [
                {
                    "title": "Pain & Frustration Analysis",
                    "icon": "FaExclamationCircle",
                    "insights": [
                        {
                            "title": "Most emotionally charged complaints",
                            "evidence": f"Users frequently express frustration about {request.topic_keyword}",
                            "source": "https://reddit.com/r/example",
                            "engagement": "150 upvotes / 30 comments",
                            "frequency": "High frequency in discussions",
                            "correlation": "Strong correlation with user satisfaction",
                            "significance": "Indicates key area for improvement",
                            "keyword": request.topic_keyword
                        }
                    ]
                },
                {
                    "title": "Question & Advice Mapping",
                    "icon": "FaQuestionCircle",
                    "insights": [
                        {
                            "title": "Common questions",
                            "evidence": f"How do I solve this {request.topic_keyword} problem?",
                            "source": "https://reddit.com/r/example2",
                            "engagement": "200 upvotes / 45 comments",
                            "frequency": "Asked weekly",
                            "correlation": "Related to user experience",
                            "significance": "Shows need for better documentation",
                            "keyword": request.topic_keyword
                        }
                    ]
                },
                {
                    "title": "Pattern Detection",
                    "icon": "FaChartLine",
                    "insights": [
                        {
                            "title": "Emerging trends",
                            "evidence": f"Growing discussion about {request.topic_keyword} alternatives",
                            "source": "https://forum.example.com",
                            "engagement": "300 upvotes / 75 comments",
                            "frequency": "Increasing trend",
                            "correlation": "Linked to market changes",
                            "significance": "Suggests market evolution",
                            "keyword": request.topic_keyword
                        }
                    ]
                },
                {
                    "title": "Main Competitors",
                    "icon": "FaBuilding",
                    "insights": [
                        {
                            "title": "Market leaders",
                            "evidence": "Company X leads with 40% market share",
                            "source": "https://market.example.com",
                            "engagement": "250 mentions",
                            "frequency": "Consistently high",
                            "correlation": "Strong brand recognition",
                            "significance": "Dominant market position",
                            "keyword": "market share"
                        }
                    ]
                }
            ]
        }
        
        logger.info("Generated mock response successfully")
        logger.debug(f"Response data: {mock_response}")
        
        return mock_response
    except Exception as e:
        logger.error(f"Error generating community insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 