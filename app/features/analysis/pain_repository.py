from sqlalchemy.ext.asyncio import AsyncSession
from ....models.pain_analysis import PainAnalysis
from .base_repository import BaseAnalysisRepository

class PainAnalysisRepository(BaseAnalysisRepository[PainAnalysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PainAnalysis) 