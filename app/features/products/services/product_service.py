from uuid import UUID
import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from ..models import ProductCreate, ProductResponse, ProductUpdate
from ..repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)

    async def create_product(self, project_id: UUID, product: ProductCreate, current_user: User) -> ProductResponse:
        try:
            product_dict = product.dict()
            db_product = await self.repository.create(product_dict, project_id, current_user.id)
            return ProductResponse.from_orm(db_product)
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_products(self, project_id: UUID, current_user: User) -> list[ProductResponse]:
        try:
            products = await self.repository.get_all_by_project(project_id, current_user.id)
            return [ProductResponse.from_orm(product) for product in products]
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_product(self, project_id: UUID, product_id: UUID, current_user: User) -> ProductResponse:
        try:
            product = await self.repository.get_by_id(product_id, project_id, current_user.id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return ProductResponse.from_orm(product)
        except Exception as e:
            logger.error(f"Error fetching product: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def update_product(self, project_id: UUID, product_id: UUID, product_update: ProductUpdate, current_user: User) -> ProductResponse:
        try:
            product = await self.repository.get_by_id(product_id, project_id, current_user.id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            update_data = product_update.dict(exclude_unset=True)
            updated_product = await self.repository.update(product, update_data)
            return ProductResponse.from_orm(updated_product)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_product(self, project_id: UUID, product_id: UUID, current_user: User) -> dict:
        try:
            product = await self.repository.get_by_id(product_id, project_id, current_user.id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            await self.repository.delete(product)
            return {"message": "Product deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e)) 