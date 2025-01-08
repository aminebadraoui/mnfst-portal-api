from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BaseInsight(BaseModel):
    title: str
    evidence: str
    query: str = ""
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class BaseAnalysisRequest(BaseModel):
    topic_keyword: str
    user_query: str
    user_id: str
    project_id: str
    source_urls: Optional[List[str]] = None
    product_urls: Optional[List[str]] = None
    use_only_specified_sources: bool = False

class BaseAnalysisResponse(BaseModel):
    status: str
    insights: List[Dict[str, Any]] = []
    error: Optional[str] = None
    raw_perplexity_response: Optional[str] = None

class BaseParserInput(BaseModel):
    content: str
    topic_keyword: str
    user_query: str 