from typing import Type, TypeVar
from sqlalchemy.orm import DeclarativeMeta
from .base import BaseAnalysisRepository
from ..models.database.pain_analysis import PainAnalysis
from ..models.database.question_analysis import QuestionAnalysis
from ..models.database.pattern_analysis import PatternAnalysis
from ..models.database.product_analysis import ProductAnalysis
from ..models.database.avatar_analysis import AvatarAnalysis

T = TypeVar('T', bound=DeclarativeMeta)

def create_repository(model_class: Type[T]) -> Type[BaseAnalysisRepository[T]]:
    """Create a repository class for a specific model."""
    class GeneratedRepository(BaseAnalysisRepository[T]):
        def __init__(self, session):
            super().__init__(session, model_class)
    
    return GeneratedRepository

# Create repository classes
PainAnalysisRepository = create_repository(PainAnalysis)
QuestionAnalysisRepository = create_repository(QuestionAnalysis)
PatternAnalysisRepository = create_repository(PatternAnalysis)
ProductAnalysisRepository = create_repository(ProductAnalysis)
AvatarAnalysisRepository = create_repository(AvatarAnalysis)

__all__ = [
    'PainAnalysisRepository',
    'QuestionAnalysisRepository',
    'PatternAnalysisRepository',
    'ProductAnalysisRepository',
    'AvatarAnalysisRepository',
] 