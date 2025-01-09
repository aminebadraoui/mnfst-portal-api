from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4, UUID as UUIDType
from sqlalchemy.orm import relationship

from .base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    # Analysis relationships
    pain_analysis = relationship("PainAnalysis", back_populates="user", cascade="all, delete-orphan")
    pattern_analysis = relationship("PatternAnalysis", back_populates="user", cascade="all, delete-orphan")
    product_analysis = relationship("ProductAnalysis", back_populates="user", cascade="all, delete-orphan")
    question_analysis = relationship("QuestionAnalysis", back_populates="user", cascade="all, delete-orphan")
    avatar_analysis = relationship("AvatarAnalysis", back_populates="user", cascade="all, delete-orphan")

    # Advertorial relationships
    story_based_advertorials = relationship("StoryBasedAdvertorial", back_populates="user", cascade="all, delete-orphan")
    value_based_advertorials = relationship("ValueBasedAdvertorial", back_populates="user", cascade="all, delete-orphan")
    informational_advertorials = relationship("InformationalAdvertorial", back_populates="user", cascade="all, delete-orphan")

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: UUIDType
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True 