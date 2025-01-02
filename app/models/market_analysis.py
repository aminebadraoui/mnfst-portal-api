from typing import List
from pydantic import BaseModel

class MarketOpportunity(BaseModel):
    """A market opportunity identified from community insights."""
    opportunity: str
    target_audience: str
    pain_points: List[str]
    potential_solutions: List[str]
    supporting_insights: List[str] 