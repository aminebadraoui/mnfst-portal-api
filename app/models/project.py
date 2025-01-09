from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    products = relationship("app.features.products.models.database.product.Product", back_populates="project", cascade="all, delete-orphan")

    # Analysis relationships
    pain_analysis = relationship("PainAnalysis", back_populates="project", cascade="all, delete-orphan")
    question_analysis = relationship("QuestionAnalysis", back_populates="project", cascade="all, delete-orphan")
    pattern_analysis = relationship("PatternAnalysis", back_populates="project", cascade="all, delete-orphan")
    product_analysis = relationship("ProductAnalysis", back_populates="project", cascade="all, delete-orphan")
    avatar_analysis = relationship("AvatarAnalysis", back_populates="project", cascade="all, delete-orphan")

    # Advertorial relationships
    story_based_advertorials = relationship("StoryBasedAdvertorial", back_populates="project", cascade="all, delete-orphan")
    value_based_advertorials = relationship("ValueBasedAdvertorial", back_populates="project", cascade="all, delete-orphan")
    informational_advertorials = relationship("InformationalAdvertorial", back_populates="project", cascade="all, delete-orphan") 