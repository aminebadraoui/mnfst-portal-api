from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class QuestionAnalysis(Base):
    __tablename__ = "question_analysis"

    # Primary key and task tracking
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    
    # Analysis metadata
    status = Column(String, nullable=False, default="processing")
    analysis_type = Column(String, nullable=False)
    query = Column(String)
    
    # Analysis results
    insights = Column(JSON, default=dict)
    raw_perplexity_response = Column(String, nullable=True)
    error = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_analysis")
    project = relationship("Project", back_populates="question_analysis")

    # Indexes
    __table_args__ = (
        Index('ix_question_analysis_user_project', 'user_id', 'project_id'),
        Index('ix_question_analysis_project_query', 'project_id', 'query'),
        Index('ix_question_analysis_task_id', 'task_id', unique=True),
    ) 