from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class CommunityInsight(Base):
    __tablename__ = "community_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, nullable=False, default="completed")  # Always completed since we append
    sections = Column(JSON, default=list)
    avatars = Column(JSON, default=list)
    error = Column(String, nullable=True)
    raw_perplexity_response = Column(String, nullable=True)
    
    # User and Project relationships - project_id is unique
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, unique=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="community_insights")
    project = relationship("Project", back_populates="community_insight", uselist=False)

    # Indexes
    __table_args__ = (
        Index('ix_community_insights_user_project', 'user_id', 'project_id'),
    ) 