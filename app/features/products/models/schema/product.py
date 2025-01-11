from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: str
    features_and_benefits: str
    guarantee: Optional[str] = None
    price: Optional[str] = None
    is_service: Optional[bool] = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    features_and_benefits: Optional[str] = None

class ProductResponse(ProductBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 