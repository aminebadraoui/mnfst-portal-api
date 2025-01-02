from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from ..models.community_analysis import CommunityInsight, CommunityTrend
from ..models.market_research import (
    MarketingResearch, CommunityAnalysis, MarketAnalysis,
    MarketingResearchResponse  # Import the Pydantic model
)
import logging

logger = logging.getLogger(__name__)

def update_research_insights_sync(research_id: str, insights: List[CommunityInsight], db: Session):
    """Update research with insights from content analysis (sync version)."""
    try:
        # Convert string ID to UUID
        uuid_id = UUID(research_id)
        
        # Get research record
        research = db.get(MarketingResearch, uuid_id)
        if not research:
            raise ValueError(f"Research {research_id} not found")
        
        # Create or update community analysis
        if not research.community_analysis:
            community_analysis = CommunityAnalysis(
                id=uuid4(),
                insights=[insight.model_dump() for insight in insights]
            )
            db.add(community_analysis)
            research.community_analysis = community_analysis
        else:
            research.community_analysis.insights = [insight.model_dump() for insight in insights]
        
        db.commit()
        
        logger.info(f"Updated research {research_id} with {len(insights)} insights")
        # Convert SQLAlchemy model to Pydantic model
        return MarketingResearchResponse.model_validate(research)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating research insights: {str(e)}")
        raise

async def update_research_insights(research_id: str, insights: List[CommunityInsight], db: AsyncSession):
    """Update research with insights from content analysis (async version)."""
    try:
        # Convert string ID to UUID
        uuid_id = UUID(research_id)
        
        # Get research record
        research = await db.get(MarketingResearch, uuid_id)
        if not research:
            raise ValueError(f"Research {research_id} not found")
        
        # Create or update community analysis
        if not research.community_analysis:
            community_analysis = CommunityAnalysis(
                id=uuid4(),
                insights=[insight.model_dump() for insight in insights]
            )
            db.add(community_analysis)
            research.community_analysis = community_analysis
        else:
            research.community_analysis.insights = [insight.model_dump() for insight in insights]
        
        await db.commit()
        
        logger.info(f"Updated research {research_id} with {len(insights)} insights")
        # Convert SQLAlchemy model to Pydantic model
        return MarketingResearchResponse.model_validate(research)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating research insights: {str(e)}")
        raise

def update_research_trends_sync(research_id: str, trends: List[CommunityTrend], db: Session):
    """Update research with market trends (sync version)."""
    try:
        # Convert string ID to UUID
        uuid_id = UUID(research_id)
        
        # Get research record
        research = db.get(MarketingResearch, uuid_id)
        if not research:
            raise ValueError(f"Research {research_id} not found")
        
        # Convert CommunityTrend to MarketOpportunity format
        opportunities = []
        for trend in trends:
            opportunity = {
                "opportunity": trend.trend,
                "target_audience": trend.affected_users,
                "pain_points": trend.pain_points,
                "potential_solutions": trend.potential_solutions,
                "supporting_insights": trend.supporting_quotes  # Use quotes as supporting insights
            }
            opportunities.append(opportunity)
        
        # Create or update market analysis
        if not research.market_analysis:
            market_analysis = MarketAnalysis(
                id=uuid4(),
                opportunities=opportunities
            )
            db.add(market_analysis)
            research.market_analysis = market_analysis
        else:
            research.market_analysis.opportunities = opportunities
        
        db.commit()
        
        logger.info(f"Updated research {research_id} with {len(trends)} trends")
        return MarketingResearchResponse.model_validate(research)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating research trends: {str(e)}")
        raise

async def update_research_trends(research_id: str, trends: List[CommunityTrend], db: AsyncSession):
    """Update research with market trends (async version)."""
    try:
        # Convert string ID to UUID
        uuid_id = UUID(research_id)
        
        # Get research record
        research = await db.get(MarketingResearch, uuid_id)
        if not research:
            raise ValueError(f"Research {research_id} not found")
        
        # Convert CommunityTrend to MarketOpportunity format
        opportunities = []
        for trend in trends:
            opportunity = {
                "opportunity": trend.trend,
                "target_audience": trend.affected_users,
                "pain_points": trend.pain_points,
                "potential_solutions": trend.potential_solutions,
                "supporting_insights": trend.supporting_quotes  # Use quotes as supporting insights
            }
            opportunities.append(opportunity)
        
        # Create or update market analysis
        if not research.market_analysis:
            market_analysis = MarketAnalysis(
                id=uuid4(),
                opportunities=opportunities
            )
            db.add(market_analysis)
            research.market_analysis = market_analysis
        else:
            research.market_analysis.opportunities = opportunities
        
        await db.commit()
        
        logger.info(f"Updated research {research_id} with {len(trends)} trends")
        return MarketingResearchResponse.model_validate(research)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating research trends: {str(e)}")
        raise 