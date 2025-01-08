from typing import List, Optional
from pydantic import Field
from .base_models import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class PainInsight(BaseInsight):
    severity: Optional[str] = None
    impact: Optional[str] = None
    potential_solutions: Optional[List[str]] = Field(default_factory=list)

class PainAnalysisRequest(BaseAnalysisRequest):
    pass

class PainAnalysisResponse(BaseAnalysisResponse):
    insights: List[PainInsight] = Field(default_factory=list)

class PainParserInput(BaseParserInput):
    pass

class PainParserResult(BaseModel):
    insights: List[PainInsight] = Field(default_factory=list) 