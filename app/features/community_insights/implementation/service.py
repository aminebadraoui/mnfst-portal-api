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
import asyncio
import json

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
                    project_id=request.project_id,
                    query=request.user_query
                )

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

            return {
                "status": "processing",
                "task_id": task.id,
                "message": "Insights generation started"
            }
        except Exception as e:
            logger.error(f"Error processing insights: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_project_insights(self, project_id: str, query: str = None) -> Optional[Dict[str, Any]]:
        """
        Get all insights for a project, optionally filtered by query.
        """
        logger.info(f"Getting insights for project {project_id}")
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                async with AsyncSessionLocal() as session:
                    repository = CommunityInsightRepository(session)
                    insights = await repository.get_project_insights(project_id, query)
                    
                    if not insights:
                        return None

                    if query:
                        # Return single insight if query is specified
                        insight = insights[0]
                        return {
                            "status": "completed",
                            "sections": insight.sections if isinstance(insight.sections, list) else json.loads(insight.sections or '[]'),
                            "avatars": insight.avatars if isinstance(insight.avatars, list) else json.loads(insight.avatars or '[]'),
                            "raw_perplexity_response": insight.raw_perplexity_response
                        }
                    else:
                        # Return all insights combined if no query specified
                        combined_sections = []
                        all_avatars = []
                        raw_responses = []

                        for insight in insights:
                            if insight.sections:
                                sections = insight.sections if isinstance(insight.sections, list) else json.loads(insight.sections or '[]')
                                combined_sections.extend(sections)
                            if insight.avatars:
                                avatars = insight.avatars if isinstance(insight.avatars, list) else json.loads(insight.avatars or '[]')
                                all_avatars.extend(avatars)
                            if insight.raw_perplexity_response:
                                raw_responses.append(insight.raw_perplexity_response)

                        return {
                            "status": "completed",
                            "sections": combined_sections,
                            "avatars": all_avatars,
                            "raw_perplexity_response": "\n\n".join(raw_responses)
                        }

            except TimeoutError:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Max retries reached for project {project_id}", exc_info=True)
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable. Please try again later."
                    )
                logger.warning(f"Timeout occurred, retrying ({retry_count}/{max_retries})")
                await asyncio.sleep(1)  # Wait before retrying
            except Exception as e:
                logger.error(f"Error getting project insights: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=str(e)
                )