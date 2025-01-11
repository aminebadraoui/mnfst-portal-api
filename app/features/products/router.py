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
from app.models.project import Project
from .models.database.product import Product
from .models.schema.product import ProductCreate, ProductResponse
from app.core.product_graph import get_product_graph_service, ProductGraphService
from app.core.product_vector import get_product_vector_service, ProductVectorService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects/{project_id}/products",
    tags=["products"]
)

@router.post("", response_model=ProductResponse)
async def create_product(
    project_id: UUID,
    product: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    graph_service: ProductGraphService = Depends(get_product_graph_service),
    vector_service: ProductVectorService = Depends(get_product_vector_service)
):
    try:
        # First verify that the project exists and belongs to the user
        project_query = select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found or you don't have access to it"
            )

        # Create product in PostgreSQL
        product_data = product.model_dump()
        if product_data.get('price'):
            product_data['price'] = Decimal(product_data['price'])
        
        db_product = Product(**product_data, user_id=current_user.id, project_id=project_id)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        # Create product node in Neo4j using the database object
        product_dict = db_product.__dict__
        if product_dict.get('price'):
            product_dict['price'] = str(product_dict['price'])
        await graph_service.create_product(product_dict)

        # Create product vectors in Qdrant using the database object
        await vector_service.create_product_vectors(product_dict)

        # Convert to response model
        return ProductResponse(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            features_and_benefits=db_product.features_and_benefits,
            guarantee=db_product.guarantee,
            price=str(db_product.price) if db_product.price else None,
            is_service=db_product.is_service,
            project_id=db_product.project_id,
            user_id=db_product.user_id,
            created_at=db_product.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the product"
        )

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
        
        # Convert to response models with proper price formatting
        return [
            ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                features_and_benefits=product.features_and_benefits,
                guarantee=product.guarantee,
                price=str(product.price) if product.price else None,
                is_service=product.is_service,
                project_id=product.project_id,
                user_id=product.user_id,
                created_at=product.created_at
            )
            for product in products
        ]
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
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            features_and_benefits=product.features_and_benefits,
            guarantee=product.guarantee,
            price=str(product.price) if product.price else None,
            is_service=product.is_service,
            project_id=product.project_id,
            user_id=product.user_id,
            created_at=product.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    project_id: UUID,
    product_id: UUID,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    graph_service: ProductGraphService = Depends(get_product_graph_service),
    vector_service: ProductVectorService = Depends(get_product_vector_service)
):
    """Update a product"""
    try:
        query = select(Product).where(
            Product.id == product_id,
            Product.project_id == project_id,
            Product.user_id == current_user.id
        )
        result = await db.execute(query)
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update product in PostgreSQL
        update_data = product.model_dump(exclude_unset=True)
        if update_data.get('price'):
            update_data['price'] = Decimal(update_data['price'])
            
        for field, value in update_data.items():
            setattr(db_product, field, value)
        await db.commit()
        await db.refresh(db_product)
        
        # Update product in Neo4j
        try:
            product_dict = db_product.__dict__
            if product_dict.get('price'):
                product_dict['price'] = str(product_dict['price'])
            await graph_service.update_product(product_dict)
        except Exception as e:
            logger.error(f"Error updating product in Neo4j: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error updating product in graph database")
        
        # Update product vectors in Qdrant
        try:
            await vector_service.update_product_vectors(product_dict)
        except Exception as e:
            logger.error(f"Error updating product vectors in Qdrant: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error updating product vectors")
        
        return ProductResponse(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            features_and_benefits=db_product.features_and_benefits,
            guarantee=db_product.guarantee,
            price=str(db_product.price) if db_product.price else None,
            is_service=db_product.is_service,
            project_id=db_product.project_id,
            user_id=db_product.user_id,
            created_at=db_product.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    graph_service: ProductGraphService = Depends(get_product_graph_service),
    vector_service: ProductVectorService = Depends(get_product_vector_service)
):
    """Delete a product"""
    try:
        query = select(Product).where(
            Product.id == product_id,
            Product.project_id == project_id,
            Product.user_id == current_user.id
        )
        result = await db.execute(query)
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Delete product from PostgreSQL
        await db.delete(db_product)
        
        # Delete product from Neo4j
        try:
            await graph_service.delete_product(str(product_id))
        except Exception as e:
            logger.error(f"Error deleting product from Neo4j: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting product from graph database")
        
        # Delete product vectors from Qdrant
        try:
            await vector_service.delete_product_vectors(str(product_id), str(current_user.id))
        except Exception as e:
            logger.error(f"Error deleting product vectors from Qdrant: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting product vectors")
        
        await db.commit()
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 