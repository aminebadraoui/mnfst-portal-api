from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from uuid import UUID

class ProductCreate(BaseModel):
    name: str
    description: str
    features_and_benefits: str
    guarantee: Optional[str] = None
    price: Optional[Decimal] = None
    is_service: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    features_and_benefits: Optional[str] = None
    guarantee: Optional[str] = None
    price: Optional[Decimal] = None
    is_service: Optional[bool] = None

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    features_and_benefits: str
    guarantee: Optional[str]
    price: Optional[Decimal]
    is_service: bool
    project_id: UUID

    class Config:
        from_attributes = True 