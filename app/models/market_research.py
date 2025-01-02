from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, ARRAY, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4, UUID as UUIDType

from ..core.database import Base
from .community_analysis import CommunityInsight as ChunkInsight
from .market_analysis import MarketOpportunity

# SQLAlchemy Models
class MarketingResearch(Base):
    __tablename__ = "marketing_research"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    name = Column(String, nullable=False)  # Research name from step 1
    source = Column(String, nullable=False)  # Selected source from step 2
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    urls = Column(ARRAY(String), default=list)
    community_analysis_id = Column(UUID, ForeignKey("community_analysis.id"), nullable=True)
    market_analysis_id = Column(UUID, ForeignKey("market_analysis.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="research")
    community_analysis = relationship("CommunityAnalysis", uselist=False)
    market_analysis = relationship("MarketAnalysis", uselist=False)

class CommunityAnalysis(Base):
    __tablename__ = "community_analysis"

    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    insights = Column(JSON)  # Will store List[ChunkInsight]

class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    opportunities = Column(JSON)  # Will store List[MarketOpportunity]

# Pydantic Models for API
class CommunityAnalysisModel(BaseModel):
    id: UUIDType
    created_at: datetime
    insights: List[ChunkInsight]
    keywords: List[str] = []

    @property
    def all_keywords(self) -> List[str]:
        """Get all unique keywords from insights."""
        keywords = []
        for insight in self.insights:
            if hasattr(insight, 'keywords'):
                keywords.extend(insight.keywords)
        return list(set(keywords))

    class Config:
        from_attributes = True

class MarketAnalysisModel(BaseModel):
    id: UUIDType
    created_at: datetime
    opportunities: List[MarketOpportunity]

    class Config:
        from_attributes = True

class MarketingResearchBase(BaseModel):
    name: str
    source: str
    urls: List[str] = []

class MarketingResearchCreate(MarketingResearchBase):
    pass

class MarketingResearchUpdate(MarketingResearchBase):
    community_analysis_id: Optional[UUIDType] = None
    market_analysis_id: Optional[UUIDType] = None

class MarketingResearchResponse(MarketingResearchBase):
    id: UUIDType
    created_at: datetime
    updated_at: datetime
    community_analysis: Optional[CommunityAnalysisModel] = None
    market_analysis: Optional[MarketAnalysisModel] = None

    @property
    def has_insights(self) -> bool:
        """Check if research has insights."""
        return (
            self.community_analysis is not None 
            and self.community_analysis.insights is not None 
            and len(self.community_analysis.insights) > 0
        )

    @property
    def keywords_found(self) -> List[str]:
        """Get all keywords from community analysis."""
        if not self.has_insights:
            return []
        return self.community_analysis.all_keywords

    class Config:
        from_attributes = True 