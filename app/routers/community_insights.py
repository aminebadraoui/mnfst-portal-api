from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from ..features.community_insights.implementation.models import CommunityInsightsResponse, CommunityInsightsRequest
from ..features.community_insights.implementation.service import CommunityInsightsService
from ..dependencies import get_community_insights_service
from ..core.notifications import listen_insight_updates
from ..utils.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db

router = APIRouter(tags=["community_insights"])

def get_service(db: Session = Depends(get_db)) -> CommunityInsightsService:
    return CommunityInsightsService(db)

@router.get("/community-insights/{project_id}", response_model=CommunityInsightsResponse)
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

@router.post("/community-insights", response_model=CommunityInsightsResponse)
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

@router.get("/community-insights/{project_id}/stream")
async def stream_project_insights(
    project_id: str,
    service: CommunityInsightsService = Depends(get_service)
) -> EventSourceResponse:
    """
    Stream community insights updates for a project.
    """
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