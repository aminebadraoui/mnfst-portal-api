from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, ARRAY, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4, UUID as UUIDType

from ..core.database import Base
from .analysis import ChunkInsight, MarketOpportunity

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
    content_analysis_id = Column(UUID, ForeignKey("content_analysis.id"), nullable=True)
    market_analysis_id = Column(UUID, ForeignKey("market_analysis.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="research")
    content_analysis = relationship("ContentAnalysis", uselist=False)
    market_analysis = relationship("MarketAnalysis", uselist=False)

class ContentAnalysis(Base):
    __tablename__ = "content_analysis"

    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    insights = Column(JSON)  # Will store List[ChunkInsight]

class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    opportunities = Column(JSON)  # Will store List[MarketOpportunity]

# Pydantic Models for API
class ContentAnalysisModel(BaseModel):
    id: UUIDType
    created_at: datetime
    insights: List[ChunkInsight]

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
    content_analysis_id: Optional[UUIDType] = None
    market_analysis_id: Optional[UUIDType] = None

class MarketingResearchResponse(MarketingResearchBase):
    id: UUIDType
    created_at: datetime
    updated_at: datetime
    content_analysis: Optional[ContentAnalysisModel] = None
    market_analysis: Optional[MarketAnalysisModel] = None

    class Config:
        from_attributes = True 