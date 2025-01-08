from sqlalchemy.ext.asyncio import AsyncSession
from ....models.avatar_analysis import AvatarAnalysis
from .base_repository import BaseAnalysisRepository

class AvatarAnalysisRepository(BaseAnalysisRepository[AvatarAnalysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AvatarAnalysis) 