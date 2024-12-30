from typing import List
from pydantic import BaseModel, HttpUrl

class RelevantQuote(BaseModel):
    text: str
    context: str = ""

class Keyword(BaseModel):
    text: str
    frequency: int

class PainPoint(BaseModel):
    description: str
    evidence: str

class MarketingAngle(BaseModel):
    title: str
    description: str
    target_audience: str

class AnalysisResponse(BaseModel):
    """Marketing analysis results from content."""
    quotes: List[RelevantQuote]
    keywords: List[Keyword]
    pain_points: List[PainPoint]
    marketing_angles: List[MarketingAngle]

class AnalysisRequest(BaseModel):
    url: HttpUrl 