from typing import List, Optional
from pydantic import BaseModel, HttpUrl

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