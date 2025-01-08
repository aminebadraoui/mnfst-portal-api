from typing import List, Optional
from pydantic import Field
from .base_models import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class ProductInsight(BaseInsight):
    platform: str
    price_range: Optional[str] = None
    positive_feedback: List[str] = Field(default_factory=list)
    negative_feedback: List[str] = Field(default_factory=list)
    market_gap: Optional[str] = None

class ProductAnalysisRequest(BaseAnalysisRequest):
    pass

class ProductAnalysisResponse(BaseAnalysisResponse):
    insights: List[ProductInsight] = Field(default_factory=list)

class ProductParserInput(BaseParserInput):
    pass

class ProductParserResult(BaseModel):
    insights: List[ProductInsight] = Field(default_factory=list) 