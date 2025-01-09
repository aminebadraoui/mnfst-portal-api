from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database.product import Product

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product_data: dict, project_id: UUID, user_id: UUID) -> Product:
        db_product = Product(
            name=product_data['name'],
            description=product_data['description'],
            features_and_benefits=product_data['features_and_benefits'],
            guarantee=product_data.get('guarantee'),
            price=product_data.get('price'),
            is_service=product_data['is_service'],
            project_id=project_id,
            user_id=user_id
        )
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def get_all_by_project(self, project_id: UUID, user_id: UUID) -> list[Product]:
        query = select(Product).where(
            Product.project_id == project_id,
            Product.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, product_id: UUID, project_id: UUID, user_id: UUID) -> Product | None:
        query = select(Product).where(
            Product.id == product_id,
            Product.project_id == project_id,
            Product.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, product: Product, update_data: dict) -> Product:
        for key, value in update_data.items():
            if value is not None:  # Only update fields that are provided
                setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit() 