from typing import List, Optional
from pydantic import BaseModel, Field

class CommunityInsightsRequest(BaseModel):
    topic_keyword: str
    source_urls: Optional[List[str]] = Field(default_factory=list)
    product_urls: Optional[List[str]] = Field(default_factory=list)
    use_only_specified_sources: bool = False

class InsightItem(BaseModel):
    title: str
    evidence: str
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class InsightSection(BaseModel):
    title: str
    icon: str
    insights: List[InsightItem] = Field(default_factory=list)

class CommunityInsightsResponse(BaseModel):
    status: str = Field(default="completed")
    sections: List[InsightSection] = Field(default_factory=list) 