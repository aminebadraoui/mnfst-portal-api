from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import uuid4, UUID as UUIDType

from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships
    research = relationship("MarketingResearch", back_populates="user")

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUIDType
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True 