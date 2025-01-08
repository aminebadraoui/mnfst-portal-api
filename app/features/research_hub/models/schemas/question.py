from typing import List, Optional
from pydantic import Field, BaseModel
from .base import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class QuestionInsight(BaseInsight):
    question_type: Optional[str] = None
    suggested_answers: Optional[List[str]] = Field(default_factory=list)
    related_questions: Optional[List[str]] = Field(default_factory=list)

class QuestionAnalysisRequest(BaseAnalysisRequest):
    pass

class QuestionAnalysisResponse(BaseAnalysisResponse):
    insights: List[QuestionInsight] = Field(default_factory=list)

class QuestionParserInput(BaseParserInput):
    pass

class QuestionParserResult(BaseModel):
    insights: List[QuestionInsight] = Field(default_factory=list) 