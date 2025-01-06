from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InsightItem(BaseModel):
    title: str
    evidence: str
    query: str = ""
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
    query: str = ""
    needs: List[str]
    pain_points: List[str]
    behaviors: List[str]

class Avatar(BaseModel):
    name: str
    type: str
    insights: List[AvatarInsight] = []

# Pain & Frustration Analysis Models
class PainInsight(BaseModel):
    title: str
    evidence: str
    query: str = ""
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class PainAnalysisResult(BaseModel):
    title: str = "Pain & Frustration Analysis"
    icon: str = "FaExclamationCircle"
    insights: List[PainInsight] = Field(default_factory=list)

# Question & Advice Mapping Models
class QuestionInsight(BaseModel):
    title: str
    evidence: str
    query: str = ""
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class QuestionMappingResult(BaseModel):
    title: str = "Question & Advice Mapping"
    icon: str = "FaQuestionCircle"
    insights: List[QuestionInsight] = Field(default_factory=list)

# Pattern Detection Models
class PatternInsight(BaseModel):
    title: str
    evidence: str
    query: str = ""
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class PatternDetectionResult(BaseModel):
    title: str = "Pattern Detection"
    icon: str = "FaChartLine"
    insights: List[PatternInsight] = Field(default_factory=list)

# Avatar Models
class AvatarProfile(BaseModel):
    title: str = "Key Characteristics"
    description: str
    evidence: str
    needs: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    behaviors: List[str] = Field(default_factory=list)

class AvatarResult(BaseModel):
    name: str
    type: str
    insights: List[AvatarProfile] = Field(default_factory=list)

class AvatarsResult(BaseModel):
    avatars: List[AvatarResult] = Field(default_factory=list)

# Combined Result Models
class ParserInput(BaseModel):
    content: str
    topic_keyword: str

class ParserResult(BaseModel):
    status: str = "completed"
    sections: List[InsightSection] = Field(default_factory=list)
    avatars: List[Avatar] = Field(default_factory=list)
    raw_perplexity_response: str = Field(default="") 

# Product Analysis Models
class ProductInsight(BaseModel):
    title: str
    platform: str
    query: str = ""
    price_range: Optional[str] = None
    positive_feedback: List[str] = Field(default_factory=list)
    negative_feedback: List[str] = Field(default_factory=list)
    market_gap: Optional[str] = None
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class ProductAnalysisResult(BaseModel):
    title: str = "Popular Products Analysis"
    icon: str = "FaShoppingCart"
    insights: List[ProductInsight] = Field(default_factory=list) 

# Failed Solutions Analysis Models
class FailedSolutionInsight(BaseModel):
    title: str
    evidence: str
    query: str = ""
    source_url: Optional[str] = None
    engagement_metrics: Optional[str] = None
    frequency: Optional[str] = None
    correlation: Optional[str] = None
    significance: Optional[str] = None

class FailedSolutionsResult(BaseModel):
    title: str = "Failed Solutions Analysis"
    icon: str = "FaTimesCircle"
    insights: List[FailedSolutionInsight] = Field(default_factory=list) 