from typing import List, Optional
from pydantic import Field, BaseModel
from .base import BaseAnalysisRequest, BaseAnalysisResponse, BaseParserInput

class Demographics(BaseModel):
    age_range: str = Field(..., description="Target age range for this segment")
    income_level: str = Field(..., description="Income bracket for this segment")
    location: str = Field(..., description="Geographic focus for this segment")
    company_size: Optional[str] = Field(None, description="Typical company size if B2B")
    industry: Optional[str] = Field(None, description="Primary industry focus")

class Engagement(BaseModel):
    frequency: int = Field(1, description="How frequently this segment appears in the data")
    representation: int = Field(10, description="Percentage representation in the data")

class AvatarProfile(BaseModel):
    """Profile model for a market segment."""
    # Market Segment Profile
    name: str = Field(..., description="Name of the market segment")
    type: str = Field(..., description="Type of segment (e.g., Enterprise Early Adopters)")
    description: str = Field(..., description="Brief overview of the segment")
    demographics: Demographics = Field(..., description="Demographic information")
    market_size: str = Field(..., description="Estimated size and growth potential")
    
    # Buying Behavior
    budget_range: str = Field(..., description="Budget range and willingness to pay")
    purchase_frequency: str = Field(..., description="Purchase frequency and timing")
    purchase_channels: List[str] = Field(default_factory=list, description="Preferred purchase channels")
    decision_makers: List[str] = Field(default_factory=list, description="Key decision makers and influencers")
    brand_preferences: List[str] = Field(default_factory=list, description="Current brand preferences")
    
    # Purchase Drivers
    pain_points: List[str] = Field(default_factory=list, description="Primary pain points and challenges")
    must_have_features: List[str] = Field(default_factory=list, description="Must-have features and requirements")
    buying_criteria: List[str] = Field(default_factory=list, description="Key buying criteria and priorities")
    deal_breakers: List[str] = Field(default_factory=list, description="Deal breakers and barriers to purchase")
    price_sensitivity: str = Field(..., description="Price sensitivity and value perception")
    
    # Competitive Landscape
    current_solutions: List[str] = Field(default_factory=list, description="Solutions currently being used")
    competitors: List[str] = Field(default_factory=list, description="Main competitors in this segment")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages")
    market_gaps: List[str] = Field(default_factory=list, description="Market gaps and opportunities")
    market_trends: List[str] = Field(default_factory=list, description="Segment-specific market trends")
    
    # Source Information
    source_url: str = Field("", description="URL where this information was found")
    engagement: Engagement = Field(default_factory=lambda: Engagement(frequency=1, representation=10))

class AvatarInsight(BaseModel):
    """Market segment insight model."""
    name: str = Field(..., description="Name of the market segment")
    type: str = Field(..., description="Category of the market segment")
    query: Optional[str] = Field(None, description="Query that generated this insight")
    profiles: List[AvatarProfile] = Field(default_factory=list, description="Detailed profiles for this segment")

class AvatarAnalysisRequest(BaseAnalysisRequest):
    pass

class AvatarAnalysisResponse(BaseAnalysisResponse):
    insights: List[AvatarInsight] = Field(default_factory=list)

class AvatarParserInput(BaseParserInput):
    pass

class AvatarParserResult(BaseModel):
    """Result model for market segment parsing."""
    insights: List[AvatarInsight] = Field(default_factory=list, description="List of market segment insights") 