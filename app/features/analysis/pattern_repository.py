from sqlalchemy.ext.asyncio import AsyncSession
from ....models.pattern_analysis import PatternAnalysis
from .base_repository import BaseAnalysisRepository

class PatternAnalysisRepository(BaseAnalysisRepository[PatternAnalysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PatternAnalysis) 