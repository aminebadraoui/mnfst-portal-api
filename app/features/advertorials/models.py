from sqlalchemy import Column, String, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base
from pydantic import BaseModel


class AdvertorialRequest(BaseModel):
    project_description: str  # JSON dump of project data
    product_description: str  # JSON dump of product data
    product_id: uuid.UUID  # For database relationship


class AdvertorialSet(BaseModel):
    story_based: dict
    informational: dict
    value_based: dict


class StoryBasedAdvertorial(Base):
    __tablename__ = "story_based_advertorials"

    # Primary key and task tracking
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    
    # Status and content
    status = Column(String, nullable=False, default="processing")
    content = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="story_based_advertorials")
    project = relationship("Project", back_populates="story_based_advertorials")
    product = relationship("app.features.products.models.database.product.Product", back_populates="story_based_advertorials")

    # Indexes
    __table_args__ = (
        Index('ix_story_based_advertorials_user_project', 'user_id', 'project_id'),
        Index('ix_story_based_advertorials_task_id', 'task_id', unique=True),
    )


class ValueBasedAdvertorial(Base):
    __tablename__ = "value_based_advertorials"

    # Primary key and task tracking
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    
    # Status and content
    status = Column(String, nullable=False, default="processing")
    content = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="value_based_advertorials")
    project = relationship("Project", back_populates="value_based_advertorials")
    product = relationship("app.features.products.models.database.product.Product", back_populates="value_based_advertorials")

    # Indexes
    __table_args__ = (
        Index('ix_value_based_advertorials_user_project', 'user_id', 'project_id'),
        Index('ix_value_based_advertorials_task_id', 'task_id', unique=True),
        Index('ix_value_based_advertorials_product_id', 'product_id'),
    )


class InformationalAdvertorial(Base):
    __tablename__ = "informational_advertorials"

    # Primary key and task tracking
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    
    # Status and content
    status = Column(String, nullable=False, default="processing")
    content = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="informational_advertorials")
    project = relationship("Project", back_populates="informational_advertorials")
    product = relationship("app.features.products.models.database.product.Product", back_populates="informational_advertorials")

    # Indexes
    __table_args__ = (
        Index('ix_informational_advertorials_user_project', 'user_id', 'project_id'),
        Index('ix_informational_advertorials_task_id', 'task_id', unique=True),
        Index('ix_informational_advertorials_product_id', 'product_id'),
    ) 