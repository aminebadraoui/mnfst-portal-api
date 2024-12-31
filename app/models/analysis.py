from typing import List
from pydantic import BaseModel, HttpUrl

class ChunkInsight(BaseModel):
    source: str
    top_keyword: str
    key_insight: str
    key_quote: str

class AnalysisRequest(BaseModel):
    urls: List[str]

class BatchAnalysisResponse(BaseModel):
    url: str
    insights: List[ChunkInsight]

class MarketAnalysisInput(BaseModel):
    keywords: List[str]
    insights: List[str]
    quotes: List[str]

class MarketOpportunity(BaseModel):
    opportunity: str
    pain_points: List[str]
    target_market: str
    potential_solutions: List[str]
    supporting_quotes: List[str]

class MarketAnalysisResponse(BaseModel):
    opportunities: List[MarketOpportunity] 