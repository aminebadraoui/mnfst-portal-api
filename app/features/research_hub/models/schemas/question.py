from typing import List, Optional
from pydantic import Field, BaseModel
from .base import BaseInsight, BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class QuestionInsight(BaseInsight):
    """A structured insight about a question or advice pattern."""
    
    title: str = Field(
        ...,
        description="Clear, descriptive title summarizing the question/advice pattern"
    )
    
    question_type: str = Field(
        ...,
        description="Category of the question (Product Usage, Troubleshooting, Comparison, etc.)"
    )
    
    evidence: str = Field(
        ...,
        description="Direct quotes showing this question/advice pattern"
    )
    
    suggested_answers: List[str] = Field(
        default_factory=list,
        description="List of most helpful/upvoted answers or solutions"
    )
    
    related_questions: List[str] = Field(
        default_factory=list,
        description="Other questions commonly asked alongside this one"
    )
    
    engagement_metrics: str = Field(
        default="",
        description="Information about question popularity and engagement"
    )
    
    source_url: str = Field(
        default="",
        description="Source where this question/advice was found"
    )

class QuestionAnalysisRequest(BaseAnalysisRequest):
    pass

class QuestionAnalysisResponse(BaseAnalysisResponse):
    insights: List[QuestionInsight] = Field(default_factory=list)

class QuestionParserInput(BaseParserInput):
    pass

class QuestionParserResult(BaseModel):
    insights: List[QuestionInsight] = Field(default_factory=list) 