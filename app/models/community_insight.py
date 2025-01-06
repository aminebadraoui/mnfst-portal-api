from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class CommunityInsight(Base):
    __tablename__ = "community_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)  # Unique task ID for tracking
    status = Column(String, nullable=False, default="completed")  # Always completed since we append
    sections = Column(JSON, default=list)
    avatars = Column(JSON, default=list)
    error = Column(String, nullable=True)
    raw_perplexity_response = Column(String, nullable=True)
    query = Column(String)
    
    # User and Project relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="community_insights")
    project = relationship("Project", back_populates="community_insights")

    # Indexes
    __table_args__ = (
        Index('ix_community_insights_user_project', 'user_id', 'project_id'),
        Index('ix_community_insights_project_query', 'project_id', 'query'),
        Index('ix_community_insights_task_id', 'task_id', unique=True),
    ) 