from typing import List, Optional
from pydantic import Field
from .base_models import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class AvatarProfile(BaseModel):
    title: str = "Key Characteristics"
    description: str
    evidence: str
    query: str = ""
    needs: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    behaviors: List[str] = Field(default_factory=list)

class AvatarInsight(BaseModel):
    name: str
    type: str
    insights: List[AvatarProfile] = Field(default_factory=list)

class AvatarAnalysisRequest(BaseAnalysisRequest):
    pass

class AvatarAnalysisResponse(BaseAnalysisResponse):
    insights: List[AvatarInsight] = Field(default_factory=list)

class AvatarParserInput(BaseParserInput):
    pass

class AvatarParserResult(BaseModel):
    insights: List[AvatarInsight] = Field(default_factory=list) 