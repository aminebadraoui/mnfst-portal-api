from fastapi import APIRouter, Depends, HTTPException
from ..features.community_insights.implementation.models import (
    CommunityInsightsRequest,
    CommunityInsightsResponse
)
from ..features.community_insights.implementation.base_models import (
    InsightItem,
    InsightSection,
    Avatar,
    AvatarInsight
)
from ..features.community_insights.implementation.service import CommunityInsightsService
from ..features.community_insights.implementation.query_generator import QueryGenerator
from typing import Dict, Optional, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.database import get_db

router = APIRouter(prefix="/api/v1")

def get_service(db: Session = Depends(get_db)) -> CommunityInsightsService:
    return CommunityInsightsService(db)

class QueryGenerationRequest(BaseModel):
    description: str

@router.post("/ai/generate-query")
async def generate_query(request: QueryGenerationRequest) -> Dict[str, str]:
    """
    Generate a community-focused query based on project description using GPT-4.
    """
    try:
        generator = QueryGenerator()
        return await generator.generate(request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/community-insights")
async def generate_community_insights(
    request: CommunityInsightsRequest,
    service: CommunityInsightsService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Process community insights and append them to the project's insights.
    """
    try:
        result = await service.process_insights(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/community-insights/{task_id}")
async def get_community_insights(
    task_id: str,
    service: CommunityInsightsService = Depends(get_service)
) -> Optional[CommunityInsightsResponse]:
    """
    Get the results of a community insights generation task.
    Returns None if the task is still processing.
    """
    try:
        result = await service.get_project_insights(task_id)
        if result is None:
            return {"status": "processing"}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 