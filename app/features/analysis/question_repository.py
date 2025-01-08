from sqlalchemy.ext.asyncio import AsyncSession
from ....models.question_analysis import QuestionAnalysis
from .base_repository import BaseAnalysisRepository

class QuestionAnalysisRepository(BaseAnalysisRepository[QuestionAnalysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, QuestionAnalysis) 