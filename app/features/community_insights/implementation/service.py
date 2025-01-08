from typing import Dict, List, Optional, Any
import logging
from .models import CommunityInsightsRequest, CommunityInsightsResponse
from .tasks import process_insights_task
from fastapi import HTTPException
from ....core.database import AsyncSessionLocal
from .repository import CommunityInsightRepository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CommunityInsightsService:
    def __init__(self, db: Session):
        self.db = db

    async def process_insights(self, request: CommunityInsightsRequest) -> Dict[str, Any]:
        """
        Initialize insight processing for a project.
        Creates an empty insight record and starts the Celery task.
        """
        logger.info(f"Initializing insights for project {request.project_id}")
        try:
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                
                # Start Celery task
                task = process_insights_task.delay(
                    topic_keyword=request.topic_keyword,
                    user_query=request.user_query,
                    user_id=request.user_id,
                    project_id=request.project_id,
                    source_urls=request.source_urls,
                    product_urls=request.product_urls,
                    use_only_specified_sources=request.use_only_specified_sources
                )
                
                task_id = task.id
                logger.info(f"Created Celery task with ID: {task_id}")
                
                # Create empty sections template
                empty_sections = [
                    {
                        "title": "Pain & Frustration Analysis",
                        "icon": "FaExclamationCircle",
                        "insights": []
                    },
                    {
                        "title": "Failed Solutions Analysis",
                        "icon": "FaTimesCircle",
                        "insights": []
                    },
                    {
                        "title": "Question & Advice Mapping",
                        "icon": "FaQuestionCircle",
                        "insights": []
                    },
                    {
                        "title": "Pattern Detection",
                        "icon": "FaChartLine",
                        "insights": []
                    },
                    {
                        "title": "Popular Products Analysis",
                        "icon": "FaShoppingCart",
                        "insights": []
                    }
                ]
                
                # Create insight with empty sections
                await repository.create_insight(
                    user_id=request.user_id,
                    project_id=request.project_id,
                    query=request.user_query,
                    task_id=task_id,
                    sections=empty_sections,
                    avatars=[],
                    raw_response=""
                )
                
                return {
                    "status": "processing",
                    "task_id": task_id,
                    "sections": empty_sections,
                    "avatars": [],
                    "raw_perplexity_response": None,
                    "message": "Insights generation started"
                }
                
        except Exception as e:
            logger.error(f"Error initializing insights: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_project_queries(self, project_id: str) -> List[str]:
        """Get all available queries for a project's community insights."""
        logger.info(f"Getting available queries for project {project_id}")
        try:
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                return await repository.get_project_queries(project_id)
        except Exception as e:
            logger.error(f"Error getting project queries: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_project_insights(self, project_id: str, query: str = None) -> Optional[Dict[str, Any]]:
        """Get all insights for a project, optionally filtered by query."""
        logger.info(f"Getting insights for project {project_id}" + (f" with query '{query}'" if query else ""))
        try:
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                return await repository.get_project_insights(project_id, query)
        except Exception as e:
            logger.error(f"Error getting project insights: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )