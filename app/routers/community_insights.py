from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from ..features.community_insights.implementation.models import CommunityInsightsRequest
from ..features.community_insights.implementation.service import CommunityInsightsService
from ..dependencies import get_community_insights_service
from ..utils.logger import logger

router = APIRouter()

@router.post("/community-insights")
async def generate_community_insights(
    request: CommunityInsightsRequest,
    service: CommunityInsightsService = Depends(get_community_insights_service)
) -> Dict[str, Any]:
    """
    Generate community insights for a given topic.
    """
    try:
        task_id = await service.generate_insights(request)
        return {"task_id": task_id}
    except Exception as e:
        logger.error(f"Error generating community insights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 