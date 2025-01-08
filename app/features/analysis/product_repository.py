from sqlalchemy.ext.asyncio import AsyncSession
from ....models.product_analysis import ProductAnalysis
from .base_repository import BaseAnalysisRepository

class ProductAnalysisRepository(BaseAnalysisRepository[ProductAnalysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProductAnalysis) 