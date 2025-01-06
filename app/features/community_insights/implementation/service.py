from typing import Dict, List, Optional, Any
import logging
from .models import CommunityInsightsRequest, CommunityInsightsResponse
from .tasks import process_insights_task
from fastapi import HTTPException
from ....core.database import AsyncSessionLocal
from .repository import CommunityInsightRepository
from sqlalchemy import select
from ....models.community_insight import CommunityInsight
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CommunityInsightsService:
    def __init__(self, db: Session):
        self.db = db

    async def process_insights(self, request: CommunityInsightsRequest) -> Dict[str, Any]:
        """
        Process insights for a project and append them to existing insights.
        """
        logger.info(f"Processing insights for project {request.project_id}")
        try:
            # Get or create insight in the database
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                insight = await repository.get_or_create_insight(
                    user_id=request.user_id,
                    project_id=request.project_id
                )

            # Start Celery task
            process_insights_task.delay(
                topic_keyword=request.topic_keyword,
                user_query=request.user_query,
                user_id=request.user_id,
                project_id=request.project_id,
                source_urls=request.source_urls,
                product_urls=request.product_urls,
                use_only_specified_sources=request.use_only_specified_sources
            )

            return {
                "status": "processing",
                "message": "Insights generation started"
            }
        except Exception as e:
            logger.error(f"Error processing insights: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_project_insights(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all insights for a project.
        """
        logger.info(f"Getting insights for project {project_id}")
        try:
            # First get the insight without user_id to get the user_id
            async with AsyncSessionLocal() as session:
                stmt = select(CommunityInsight).where(CommunityInsight.project_id == project_id)
                result = await session.execute(stmt)
                insight = result.scalar_one_or_none()
                if insight:
                    return {
                        "status": "completed",
                        "sections": insight.sections,
                        "avatars": insight.avatars,
                        "raw_perplexity_response": insight.raw_perplexity_response
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting project insights: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )