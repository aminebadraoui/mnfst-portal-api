from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    features_and_benefits = Column(Text, nullable=False)  # Store as JSON string
    guarantee = Column(Text)
    price = Column(Numeric(10, 2))  # Allow for decimal prices
    is_service = Column(Boolean, default=False)  # True if it's a service, False if it's a product
    
    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="products")
    user = relationship("User", back_populates="products")
    story_based_advertorials = relationship("app.features.advertorials.models.StoryBasedAdvertorial", back_populates="product")
    value_based_advertorials = relationship("app.features.advertorials.models.ValueBasedAdvertorial", back_populates="product")
    informational_advertorials = relationship("app.features.advertorials.models.InformationalAdvertorial", back_populates="product")

    # Indexes
    __table_args__ = (
        # Index for faster lookups by project
        Index('ix_products_project_id', 'project_id'),
    ) 