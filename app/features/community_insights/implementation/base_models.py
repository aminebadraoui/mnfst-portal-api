from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

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
    insights: List[Dict[str, Any]] = []

class AvatarInsight(BaseModel):
    title: str
    description: str
    evidence: str
    needs: List[str]
    pain_points: List[str]
    behaviors: List[str]

class Avatar(BaseModel):
    name: str
    type: str
    insights: List[AvatarInsight] = []

class ParserInput(BaseModel):
    content: str
    topic_keyword: str

class ParserResult(BaseModel):
    status: str = "completed"
    sections: List[InsightSection] = []
    avatars: List[Avatar] = []
    raw_perplexity_response: str = "" 