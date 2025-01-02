from typing import List
from pydantic import BaseModel

class CommunityInsight(BaseModel):
    """An insight extracted from community content."""
    source: str
    pain_point: str
    key_insight: str
    supporting_quote: str

class AnalysisRequest(BaseModel):
    """Request to analyze community content from URLs."""
    urls: List[str]

class CommunityAnalysisResponse(BaseModel):
    """Response containing insights from community content."""
    url: str
    insights: List[CommunityInsight]

class CommunityTrendsInput(BaseModel):
    """Input for analyzing community trends."""
    insights: List[str]
    quotes: List[str]
    keywords_found: List[str] = []

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