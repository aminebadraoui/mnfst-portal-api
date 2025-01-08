from typing import List, Optional, Type, TypeVar, Generic, Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from uuid import UUID

class AnalysisModel(Protocol):
    """Protocol defining the required attributes for analysis models."""
    id: UUID
    task_id: UUID
    user_id: UUID
    project_id: UUID
    query: str
    insights: dict
    raw_perplexity_response: str
    analysis_type: str
    status: str
    error: Optional[str]
    created_at: str

T = TypeVar('T', bound=DeclarativeMeta)

class BaseAnalysisRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(
        self,
        user_id: str,
        project_id: str,
        query: str,
        insights: dict,
        raw_perplexity_response: str,
        analysis_type: str
    ) -> T:
        """Create a new analysis record."""
        analysis = self.model(
            user_id=user_id,
            project_id=project_id,
            query=query,
            insights=insights,
            raw_perplexity_response=raw_perplexity_response,
            analysis_type=analysis_type
        )
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    async def get_by_task_id(self, task_id: str, analysis_type: str) -> Optional[T]:
        """Get analysis by task ID and type."""
        query = select(self.model).where(
            self.model.task_id == task_id,
            self.model.analysis_type == analysis_type
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: str,
        user_id: str,
        analysis_type: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[T]:
        """Get all analyses for a project of a specific type."""
        query = (
            select(self.model)
            .where(
                self.model.project_id == project_id,
                self.model.user_id == user_id,
                self.model.analysis_type == analysis_type
            )
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_project_queries(self, project_id: str) -> List[str]:
        """Get all unique queries for a project."""
        query = (
            select(self.model.query)
            .where(self.model.project_id == project_id)
            .distinct()
            .order_by(self.model.query)
        )
        result = await self.session.execute(query)
        return [query[0] for query in result.all() if query[0]] 