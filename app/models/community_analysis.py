from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Union

class CommunityInsight(BaseModel):
    """An insight extracted from community content."""
    source: str
    pain_point: str
    key_insight: str
    supporting_quote: str
    keywords: List[str] = []  # Add keywords field with default empty list

class AnalysisRequest(BaseModel):
    """Request for content analysis."""
    research_id: Union[str, UUID]  # Accept either string or UUID
    urls: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "73aea148-cd3a-4b2c-be8a-7931f6dbaeb2",
                "urls": ["https://example.com"]
            }
        }

class CommunityAnalysisResponse(BaseModel):
    """Response containing insights from community content."""
    url: str
    insights: List[CommunityInsight]

class CommunityTrendsInput(BaseModel):
    """Input for trends analysis."""
    research_id: Union[str, UUID]  # Accept either string or UUID
    insights: List[str]
    quotes: List[str]
    keywords_found: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "73aea148-cd3a-4b2c-be8a-7931f6dbaeb2",
                "insights": ["insight1", "insight2"],
                "quotes": ["quote1", "quote2"],
                "keywords_found": []
            }
        }

class CommunityTrend(BaseModel):
    """A trend identified in community discussions."""
    trend: str
    pain_points: List[str]
    affected_users: str
    potential_solutions: List[str]
    supporting_quotes: List[str]

class CommunityTrendsResponse(BaseModel):
    """Response containing identified community trends."""
    trends: List[CommunityTrend] 