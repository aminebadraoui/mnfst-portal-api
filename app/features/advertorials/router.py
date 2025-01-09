from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from .service import generate_advertorials
from .models import StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class AdvertorialRequest(BaseModel):
    description: str


router = APIRouter(
    prefix="/projects/{project_id}/advertorials",
    tags=["advertorials"]
)


@router.post("/generate")
async def create_advertorials(
    project_id: UUID,
    request: AdvertorialRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate all three types of advertorials for a project"""
    logger.info(f"Received advertorial generation request for project {project_id}")
    logger.debug(f"Request data: {request.dict()}")
    logger.debug(f"Current user: {current_user}")

    try:
        story_id, value_id, info_id = await generate_advertorials(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            description=request.description
        )
        logger.info("Successfully generated all advertorials")
        return {
            "story_based_id": story_id,
            "value_based_id": value_id,
            "informational_id": info_id
        }
    except Exception as e:
        logger.error(f"Error in advertorial generation endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{advertorial_id}")
async def get_advertorial(
    project_id: UUID,
    advertorial_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific advertorial by ID"""
    # Try each advertorial type
    for model in [StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial]:
        query = select(model).where(
            model.id == advertorial_id,
            model.project_id == project_id,
            model.user_id == current_user.id
        )
        result = await db.execute(query)
        advertorial = result.scalar_one_or_none()
        if advertorial:
            return {
                "id": advertorial.id,
                "type": model.__name__,
                "status": advertorial.status,
                "content": advertorial.content,
                "error": advertorial.error,
                "created_at": advertorial.created_at,
                "updated_at": advertorial.updated_at
            }
    
    raise HTTPException(status_code=404, detail="Advertorial not found") 


@router.get("")
async def get_advertorials(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all advertorials for a project"""
    try:
        # Query all types of advertorials for the project
        story_query = select(StoryBasedAdvertorial).where(StoryBasedAdvertorial.project_id == project_id)
        value_query = select(ValueBasedAdvertorial).where(ValueBasedAdvertorial.project_id == project_id)
        info_query = select(InformationalAdvertorial).where(InformationalAdvertorial.project_id == project_id)

        # Execute queries
        story_result = await db.execute(story_query)
        value_result = await db.execute(value_query)
        info_result = await db.execute(info_query)

        # Get all results
        story_ads = story_result.scalars().all()
        value_ads = value_result.scalars().all()
        info_ads = info_result.scalars().all()

        return {
            "story_based": [{"id": ad.id, "status": ad.status, "content": ad.content, "error": ad.error} for ad in story_ads],
            "value_based": [{"id": ad.id, "status": ad.status, "content": ad.content, "error": ad.error} for ad in value_ads],
            "informational": [{"id": ad.id, "status": ad.status, "content": ad.content, "error": ad.error} for ad in info_ads]
        }
    except Exception as e:
        logger.error(f"Error fetching advertorials: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 


@router.delete("")
async def delete_all_advertorials(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all advertorials for a project"""
    try:
        # Delete all types of advertorials for the project
        for model in [StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial]:
            query = select(model).where(
                model.project_id == project_id,
                model.user_id == current_user.id
            )
            result = await db.execute(query)
            advertorials = result.scalars().all()
            
            for ad in advertorials:
                await db.delete(ad)
        
        await db.commit()
        return {"message": "All advertorials deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting advertorials: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 