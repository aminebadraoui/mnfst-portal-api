from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.product import Product

logger = logging.getLogger(__name__)

class ProductCreate(BaseModel):
    name: str
    description: str
    features_and_benefits: List[str]
    guarantee: Optional[str] = None
    price: Optional[Decimal] = None
    is_service: bool = False

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    features_and_benefits: List[str]
    guarantee: Optional[str]
    price: Optional[Decimal]
    is_service: bool
    project_id: UUID

    class Config:
        from_attributes = True

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
    logger.info(f"Received product creation request for project {project_id}")
    logger.debug(f"Request data: {product.model_dump()}")
    logger.debug(f"Current user: {current_user.id}")
    
    try:
        logger.debug("Creating product with data:")
        logger.debug(f"  Name: {product.name}")
        logger.debug(f"  Description: {product.description}")
        logger.debug(f"  Features and Benefits: {product.features_and_benefits}")
        logger.debug(f"  Guarantee: {product.guarantee}")
        logger.debug(f"  Price: {product.price}")
        logger.debug(f"  Is Service: {product.is_service}")
        
        db_product = Product(
            name=product.name,
            description=product.description,
            features_and_benefits=product.features_and_benefits,
            guarantee=product.guarantee,
            price=product.price,
            is_service=product.is_service,
            project_id=project_id,
            user_id=current_user.id
        )
        logger.debug("Product object created, adding to database")
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        logger.info("Product successfully created")
        return db_product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ProductResponse])
async def get_products(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all products for a project"""
    try:
        query = select(Product).where(
            Product.project_id == project_id,
            Product.user_id == current_user.id
        )
        result = await db.execute(query)
        products = result.scalars().all()
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    project_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product"""
    try:
        query = select(Product).where(
            Product.id == product_id,
            Product.project_id == project_id,
            Product.user_id == current_user.id
        )
        result = await db.execute(query)
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    try:
        query = select(Product).where(
            Product.id == product_id,
            Product.project_id == project_id,
            Product.user_id == current_user.id
        )
        result = await db.execute(query)
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        await db.delete(product)
        await db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 