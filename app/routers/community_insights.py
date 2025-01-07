from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sse_starlette.sse import EventSourceResponse
from ..features.community_insights.implementation.models import CommunityInsightsResponse, CommunityInsightsRequest
from ..features.community_insights.implementation.service import CommunityInsightsService
from ..core.notifications import listen_insight_updates
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.celery import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/community-insights", tags=["community_insights"])

def get_service(db: Session = Depends(get_db)) -> CommunityInsightsService:
    return CommunityInsightsService(db)

# Task status endpoint first to avoid path conflicts
@router.get("/tasks/{task_id}", response_model=CommunityInsightsResponse)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    try:
        # Get task result from Celery
        task = celery_app.AsyncResult(task_id)
        logger.info(f"Checking task {task_id} - State: {task.state}")
        
        if task.ready():
            # Task is complete, return the result
            result = task.get()
            logger.info(f"Task {task_id} completed - Result: {result}")
            return result
        else:
            # Task is still processing
            response = {
                "status": "processing",
                "message": f"Task is still processing - State: {task.state}"
            }
            logger.info(f"Task {task_id} in progress - Response: {response}")
            return response
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=CommunityInsightsResponse)
async def generate_project_community_insight(
    request: CommunityInsightsRequest,
    service: CommunityInsightsService = Depends(get_service)
):
    """Generate community insights for a project."""
    try:
        insights = await service.process_insights(request)
        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=CommunityInsightsResponse)
def get_project_community_insight(
    project_id: str,
    service: CommunityInsightsService = Depends(get_service)
):
    """Get community insights for a project."""
    try:
        insights = service.get_project_insights(project_id)
        if insights is None:
            raise HTTPException(status_code=404, detail="No insights found for this project")
        return insights
    except Exception as e:
        logger.error(f"Error getting project insights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{project_id}/stream")
async def stream_project_insights(
    project_id: str,
    service: CommunityInsightsService = Depends(get_service)
) -> EventSourceResponse:
    """Stream community insights updates for a project."""
    try:
        # Get initial state
        insight = service.get_project_insights(project_id)
        if insight is None:
            raise HTTPException(status_code=404, detail="No insights found for this project")

        async def event_generator():
            # Send initial state
            yield {
                "event": "initial",
                "data": insight
            }

            # Listen for updates
            async for update in listen_insight_updates(project_id):
                yield {
                    "event": "update",
                    "data": update
                }

        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error streaming insights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{project_id}/community-insights/queries")
async def get_project_queries(
    project_id: str,
    db: Session = Depends(get_db)
) -> List[str]:
    """Get all available queries for a project's community insights."""
    service = CommunityInsightsService(db)
    queries = await service.get_project_queries(project_id)
    return queries

@router.get("/{project_id}/community-insights")
async def get_project_insights(
    project_id: str,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get community insights for a project, optionally filtered by query."""
    service = CommunityInsightsService(db)
    insights = await service.get_project_insights(project_id, query)
    if not insights:
        raise HTTPException(status_code=404, detail="No community insights found")
    return insights 