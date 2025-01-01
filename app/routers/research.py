from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Dict
import logging
from uuid import UUID

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.research import (
    MarketingResearchCreate,
    MarketingResearchUpdate,
    MarketingResearchResponse
)
from ..models.analysis import ChunkInsight, MarketOpportunity
from ..services.research import ResearchService
from ..models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=MarketingResearchResponse)
async def create_research(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new marketing research."""
    try:
        service = ResearchService(db)
        research = await service.create_research(current_user.id)
        return research
    except Exception as e:
        logger.error(f"Error creating research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[MarketingResearchResponse])
async def list_research(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all research for the current user."""
    try:
        service = ResearchService(db)
        research_list = await service.list_research(current_user.id)
        return research_list
    except Exception as e:
        logger.error(f"Error listing research: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing research: {str(e)}"
        )

@router.get("/{research_id}", response_model=MarketingResearchResponse)
async def get_research(
    research_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific research by ID."""
    try:
        service = ResearchService(db)
        research = await service.get_research(research_id, current_user.id)
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        return research
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting research: {str(e)}"
        )

@router.put("/{research_id}/urls", response_model=MarketingResearchResponse)
async def update_research_urls(
    research_id: UUID,
    data: Union[List[str], Dict] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the URLs of a research."""
    try:
        # Handle both formats: direct array or {urls: array}
        urls = data if isinstance(data, list) else data.get('urls', [])
        
        service = ResearchService(db)
        research = await service.update_research_urls(research_id, current_user.id, urls)
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        return research
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating research URLs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating research URLs: {str(e)}"
        )

@router.post("/{research_id}/content-analysis", response_model=MarketingResearchResponse)
async def save_content_analysis(
    research_id: UUID,
    insights: List[ChunkInsight],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save content analysis results."""
    try:
        service = ResearchService(db)
        research = await service.save_content_analysis(research_id, current_user.id, insights)
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        return research
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving content analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving content analysis: {str(e)}"
        )

@router.post("/{research_id}/market-analysis", response_model=MarketingResearchResponse)
async def save_market_analysis(
    research_id: UUID,
    opportunities: List[MarketOpportunity],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save market analysis results."""
    try:
        service = ResearchService(db)
        research = await service.save_market_analysis(research_id, current_user.id, opportunities)
        if not research:
            raise HTTPException(status_code=404, detail="Research not found")
        return research
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving market analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving market analysis: {str(e)}"
        )

@router.delete("/{research_id}", response_model=dict)
async def delete_research(
    research_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific research entry."""
    try:
        service = ResearchService(db)
        await service.delete_research(research_id, current_user.id)
        return {"message": "Research deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting research: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting research: {str(e)}"
        ) 