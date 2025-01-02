from celery import shared_task
from typing import List
import asyncio
from .agents.insights import analyze_chunk as analyze_insights_chunk
from .agents.trends import analyze_trends
from .models.community_analysis import CommunityInsight, CommunityTrend
from .services.research import update_research_insights_sync, update_research_trends_sync
from .services.scraper import scrape_and_chunk_content
from .models.scraper import ContentChunk
from .db.session import get_sync_db
import logging

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper function to run async code in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@shared_task(bind=True)
def analyze_content_task(self, research_id: str, urls: List[str]):
    """Background task to analyze content from URLs."""
    try:
        logger.info(f"Starting content analysis for research {research_id}")
        insights = []
        db = get_sync_db()
        updated_research = None
        
        async def process_urls():
            for url in urls:
                try:
                    # First scrape and chunk the content
                    chunks = await scrape_and_chunk_content(url)
                    if not chunks:
                        logger.warning(f"No content chunks found for URL {url}")
                        continue
                    
                    logger.info(f"Processing {len(chunks)} chunks from URL {url}")
                    
                    # Analyze each chunk
                    for chunk in chunks:
                        try:
                            # Ensure chunk is properly formatted
                            if not isinstance(chunk, ContentChunk):
                                logger.warning(f"Invalid chunk type for URL {url}: {type(chunk)}")
                                continue
                                
                            chunk_insight = await analyze_insights_chunk(chunk)
                            if chunk_insight:
                                insights.append(chunk_insight)
                                logger.debug(f"Added insight from chunk {chunk.chunk_number}")
                        except Exception as chunk_error:
                            logger.error(f"Error processing chunk {getattr(chunk, 'chunk_number', 'unknown')} from {url}: {str(chunk_error)}")
                            continue
                    
                    # Update research with partial results
                    if insights:
                        updated_research = update_research_insights_sync(research_id, insights, db)
                    
                except Exception as e:
                    logger.error(f"Error analyzing URL {url}: {str(e)}")
                    continue
            
            return updated_research
        
        try:
            # Run async code in a new event loop
            updated_research = run_async(process_urls())
        finally:
            db.close()
        
        logger.info(f"Content analysis complete for research {research_id}")
        return {
            "status": "completed",
            "insights_count": len(insights),
            "data": {
                "research_id": research_id,
                "insights": [insight.model_dump() for insight in insights] if insights else []
            }
        }
        
    except Exception as e:
        logger.error(f"Error in content analysis task: {str(e)}")
        return {"status": "failed", "error": str(e)}

@shared_task(bind=True)
def analyze_market_task(self, research_id: str, insights: List[str], quotes: List[str], keywords_found: List[str]):
    """Background task to analyze market opportunities."""
    try:
        logger.info(f"Starting market analysis for research {research_id}")
        db = get_sync_db()
        
        async def process_analysis():
            # Analyze trends
            trends = await analyze_trends(insights, quotes, keywords_found)
            
            # Update research with trends
            updated_research = update_research_trends_sync(research_id, trends, db)
            return trends, updated_research
        
        try:
            # Run async code in a new event loop
            trends, updated_research = run_async(process_analysis())
        finally:
            db.close()
        
        logger.info(f"Market analysis complete for research {research_id}")
        return {
            "status": "completed",
            "trends_count": len(trends),
            "data": {
                "research_id": research_id,
                "trends": [trend.model_dump() for trend in trends] if trends else []
            }
        }
        
    except Exception as e:
        logger.error(f"Error in market analysis task: {str(e)}")
        return {"status": "failed", "error": str(e)} 