from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from .models import ProductCreate, ProductResponse, ProductUpdate
from .services.product_service import ProductService

router = APIRouter(
    prefix="/projects/{project_id}/products",
    tags=["products"]
)

@router.post("", response_model=ProductResponse)
async def create_product(
    project_id: UUID,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product or service"""
    service = ProductService(db)
    return await service.create_product(project_id, product, current_user)

@router.get("", response_model=List[ProductResponse])
async def get_products(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all products for a project"""
    service = ProductService(db)
    return await service.get_products(project_id, current_user)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    project_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product"""
    service = ProductService(db)
    return await service.get_product(project_id, product_id, current_user)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    project_id: UUID,
    product_id: UUID,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    service = ProductService(db)
    return await service.update_product(project_id, product_id, product, current_user)

@router.delete("/{product_id}")
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    service = ProductService(db)
    return await service.delete_product(project_id, product_id, current_user) 