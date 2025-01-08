import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories import (
    PainAnalysisRepository,
    QuestionAnalysisRepository,
    PatternAnalysisRepository,
    ProductAnalysisRepository,
    AvatarAnalysisRepository
)
from ..tasks.processor import process_analysis_task
from ...core.celery import celery_app

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pain_repository = PainAnalysisRepository(session)
        self.question_repository = QuestionAnalysisRepository(session)
        self.pattern_repository = PatternAnalysisRepository(session)
        self.product_repository = ProductAnalysisRepository(session)
        self.avatar_repository = AvatarAnalysisRepository(session)

    async def start_analysis(
        self,
        user_id: str,
        project_id: str,
        topic_keyword: str,
        user_query: str,
        analysis_type: str,
        source_urls: List[str] = None,
        product_urls: List[str] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Start an analysis task."""
        logger.info(f"Starting {analysis_type} analysis for project {project_id}")
        
        # Map analysis types to their repositories
        repository_map = {
            "pain": self.pain_repository,
            "question": self.question_repository,
            "pattern": self.pattern_repository,
            "product": self.product_repository,
            "avatar": self.avatar_repository
        }
        
        # Get the appropriate repository
        repository = repository_map.get(analysis_type)
        if not repository:
            raise ValueError(f"Invalid analysis type: {analysis_type}")
        
        # Start Celery task
        task = celery_app.send_task(
            "process_analysis_task",
            args=[
                user_id,
                project_id,
                topic_keyword,
                user_query,
                analysis_type,
                source_urls,
                product_urls,
                use_only_specified_sources
            ]
        )
        
        return {
            "task_id": task.id,
            "status": "processing"
        }

    async def get_analysis_results(
        self,
        project_id: str,
        analysis_type: str,
        query: str = None,
        task_id: str = None
    ) -> Dict[str, Any]:
        """Get analysis results."""
        logger.info(f"Getting {analysis_type} analysis results for project {project_id}")
        
        # Map analysis types to their repositories
        repository_map = {
            "pain": self.pain_repository,
            "question": self.question_repository,
            "pattern": self.pattern_repository,
            "product": self.product_repository,
            "avatar": self.avatar_repository
        }
        
        # Get the appropriate repository
        repository = repository_map.get(analysis_type)
        if not repository:
            raise ValueError(f"Invalid analysis type: {analysis_type}")
        
        return await repository.get_insights(
            project_id=project_id,
            query=query,
            task_id=task_id
        ) 