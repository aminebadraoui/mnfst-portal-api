import logging
from typing import Optional
from .models import CommunityInsightsRequest, CommunityInsightsResponse
from .tasks import process_community_insights
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CommunityInsightsService:
    async def generate_insights(self, request: CommunityInsightsRequest) -> str:
        """
        Start a Celery task to generate and parse community insights.
        Returns a task ID that can be used to fetch the results.
        """
        try:
            logger.info(f"Starting insights generation for topic: {request.topic_keyword}")
            
            # Start async task for processing
            task = process_community_insights.delay(
                topic_keyword=request.topic_keyword,
                source_urls=request.source_urls,
                product_urls=request.product_urls,
                use_only_specified_sources=request.use_only_specified_sources
            )
            logger.info(f"Started task with ID: {task.id}")
            
            return task.id
            
        except Exception as e:
            logger.error(f"Error starting insights task: {str(e)}", exc_info=True)
            raise

    async def get_task_result(self, task_id: str) -> CommunityInsightsResponse:
        """
        Get the result of a processing task by its ID.
        Returns a CommunityInsightsResponse with either processing status or completed results.
        """
        try:
            logger.info(f"Fetching result for task: {task_id}")
            task = process_community_insights.AsyncResult(task_id)
            
            if task.ready():
                if task.successful():
                    result = task.get()
                    return CommunityInsightsResponse(
                        status="completed",
                        sections=result.get("sections", [])
                    )
                else:
                    logger.error(f"Task failed: {task.result}")
                    raise HTTPException(status_code=500, detail="Task processing failed")
            else:
                logger.info(f"Task {task_id} is still processing")
                return CommunityInsightsResponse(status="processing")
                
        except Exception as e:
            logger.error(f"Error getting task result: {str(e)}", exc_info=True)
            raise 