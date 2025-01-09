from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial


class StoryBasedAdvertorialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, project_id: UUID, user_id: UUID, product_id: UUID) -> StoryBasedAdvertorial:
        advertorial = StoryBasedAdvertorial(
            project_id=project_id,
            user_id=user_id,
            product_id=product_id,
            status="pending"
        )
        self.db.add(advertorial)
        await self.db.flush()
        return advertorial

    async def update_content(self, id: UUID, content: dict) -> StoryBasedAdvertorial:
        query = select(StoryBasedAdvertorial).where(StoryBasedAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.content = content
        advertorial.status = "completed"
        await self.db.flush()
        return advertorial

    async def update_error(self, id: UUID, error: str) -> StoryBasedAdvertorial:
        query = select(StoryBasedAdvertorial).where(StoryBasedAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.error = error
        advertorial.status = "failed"
        await self.db.flush()
        return advertorial


class ValueBasedAdvertorialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, project_id: UUID, user_id: UUID, product_id: UUID) -> ValueBasedAdvertorial:
        advertorial = ValueBasedAdvertorial(
            project_id=project_id,
            user_id=user_id,
            product_id=product_id,
            status="pending"
        )
        self.db.add(advertorial)
        await self.db.flush()
        return advertorial

    async def update_content(self, id: UUID, content: dict) -> ValueBasedAdvertorial:
        query = select(ValueBasedAdvertorial).where(ValueBasedAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.content = content
        advertorial.status = "completed"
        await self.db.flush()
        return advertorial

    async def update_error(self, id: UUID, error: str) -> ValueBasedAdvertorial:
        query = select(ValueBasedAdvertorial).where(ValueBasedAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.error = error
        advertorial.status = "failed"
        await self.db.flush()
        return advertorial


class InformationalAdvertorialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, project_id: UUID, user_id: UUID, product_id: UUID) -> InformationalAdvertorial:
        advertorial = InformationalAdvertorial(
            project_id=project_id,
            user_id=user_id,
            product_id=product_id,
            status="pending"
        )
        self.db.add(advertorial)
        await self.db.flush()
        return advertorial

    async def update_content(self, id: UUID, content: dict) -> InformationalAdvertorial:
        query = select(InformationalAdvertorial).where(InformationalAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.content = content
        advertorial.status = "completed"
        await self.db.flush()
        return advertorial

    async def update_error(self, id: UUID, error: str) -> InformationalAdvertorial:
        query = select(InformationalAdvertorial).where(InformationalAdvertorial.id == id)
        result = await self.db.execute(query)
        advertorial = result.scalar_one()
        advertorial.error = error
        advertorial.status = "failed"
        await self.db.flush()
        return advertorial 