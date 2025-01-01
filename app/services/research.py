from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from uuid import UUID

from ..models.research import (
    MarketingResearch,
    ContentAnalysis,
    MarketAnalysis,
    MarketingResearchCreate,
    MarketingResearchUpdate
)
from ..models.analysis import ChunkInsight, MarketOpportunity

class ResearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_research(self, user_id: UUID) -> MarketingResearch:
        """Create a new empty marketing research."""
        research = MarketingResearch(user_id=user_id)
        self.db.add(research)
        await self.db.commit()
        await self.db.refresh(research)
        return research

    async def get_research(self, research_id: UUID, user_id: UUID) -> Optional[MarketingResearch]:
        """Get a research by ID and verify user ownership."""
        query = select(MarketingResearch).where(
            MarketingResearch.id == research_id,
            MarketingResearch.user_id == user_id
        ).options(
            joinedload(MarketingResearch.content_analysis),
            joinedload(MarketingResearch.market_analysis)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_research(self, user_id: UUID) -> List[MarketingResearch]:
        """List all research for a user."""
        query = select(MarketingResearch).where(
            MarketingResearch.user_id == user_id
        ).options(
            joinedload(MarketingResearch.content_analysis),
            joinedload(MarketingResearch.market_analysis)
        ).order_by(MarketingResearch.updated_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_research_urls(self, research_id: UUID, user_id: UUID, urls: List[str]) -> Optional[MarketingResearch]:
        """Update the URLs of a research."""
        research = await self.get_research(research_id, user_id)
        if not research:
            return None
        
        research.urls = urls
        research.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(research)
        return research

    async def save_content_analysis(
        self, research_id: UUID, user_id: UUID, insights: List[ChunkInsight]
    ) -> Optional[MarketingResearch]:
        """Save content analysis results."""
        research = await self.get_research(research_id, user_id)
        if not research:
            return None

        # Create content analysis
        content_analysis = ContentAnalysis(insights=[insight.model_dump() for insight in insights])
        self.db.add(content_analysis)
        await self.db.flush()  # Get the ID without committing

        # Update research
        research.content_analysis_id = content_analysis.id
        research.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(research)
        return research

    async def save_market_analysis(
        self, research_id: UUID, user_id: UUID, opportunities: List[MarketOpportunity]
    ) -> Optional[MarketingResearch]:
        """Save market analysis results."""
        research = await self.get_research(research_id, user_id)
        if not research:
            return None

        # Create market analysis
        market_analysis = MarketAnalysis(opportunities=[opp.model_dump() for opp in opportunities])
        self.db.add(market_analysis)
        await self.db.flush()  # Get the ID without committing

        # Update research
        research.market_analysis_id = market_analysis.id
        research.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(research)
        return research 

    async def delete_research(self, research_id: UUID, user_id: UUID) -> None:
        """Delete a specific research entry."""
        research = await self.get_research(research_id, user_id)
        if not research:
            raise ValueError("Research not found")
            
        await self.db.delete(research)
        await self.db.commit() 