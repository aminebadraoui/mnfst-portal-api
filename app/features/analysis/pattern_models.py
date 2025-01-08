from typing import List, Optional
from pydantic import Field
from .base_models import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class PatternInsight(BaseInsight):
    pattern_type: Optional[str] = None
    trend_direction: Optional[str] = None
    supporting_data: Optional[List[str]] = Field(default_factory=list)
    implications: Optional[List[str]] = Field(default_factory=list)

class PatternAnalysisRequest(BaseAnalysisRequest):
    pass

class PatternAnalysisResponse(BaseAnalysisResponse):
    insights: List[PatternInsight] = Field(default_factory=list)

class PatternParserInput(BaseParserInput):
    pass

class PatternParserResult(BaseModel):
    insights: List[PatternInsight] = Field(default_factory=list) 