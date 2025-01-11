from typing import List, Optional, Dict
from pydantic import Field, BaseModel

class PainInsight(BaseModel):
    title: str = Field(..., description="Clear title describing the pain point")
    severity: str = Field(..., description="Pain point severity: critical, major, or minor")
    pain_quote: str = Field(..., description="Direct quote showing the pain point")
    impact: str = Field(..., description="Description of impact on user experience")
    impact_quote: str = Field(..., description="Supporting quote for impact")
    workaround: Optional[str] = Field(None, description="Common workaround if available")
    workaround_quote: Optional[str] = Field(None, description="Example quote for workaround")
    source_url: str = Field(..., description="Source URL where this pain point was found")
    engagement: Dict[str, int] = Field(
        default_factory=lambda: {"upvotes": 0, "comments": 0},
        description="Engagement metrics including upvotes and comments"
    )
    query: Optional[str] = Field(None, description="The query that generated this insight")

class PainParserResult(BaseModel):
    insights: List[PainInsight] = Field(default_factory=list) 