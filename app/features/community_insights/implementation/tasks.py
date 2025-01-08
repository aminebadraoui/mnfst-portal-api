from typing import Dict, List, Optional, Any
import logging
from celery import shared_task
from .parser import PerplexityParser
from .repository import CommunityInsightRepository
from ....core.config import settings
from ....core.celery import celery_app
from ....core.database import AsyncSessionLocal
import asyncio
import json
import traceback
from celery.exceptions import TaskError
from .perplexity import PerplexityClient
from sqlalchemy.sql import select
from ....models.community_insight import CommunityInsight

logger = logging.getLogger(__name__)

class InsightProcessingError(TaskError):
    """Custom exception for insight processing errors"""
    pass

@shared_task(bind=True)
def process_insights_task(
    self,
    project_id: str,
    user_id: str,
    topic_keyword: str,
    user_query: str,
    source_urls: Optional[List[str]] = None,
    product_urls: Optional[List[str]] = None,
    use_only_specified_sources: bool = False
) -> Dict[str, Any]:
    """
    Celery task to process community insights.
    Processes each section independently and updates the database after each section.
    Flow: perplexity research -> parser agent -> update community insight -> update database
    """
    task_id = self.request.id
    logger.info(f"Starting process_insights_task with task_id: {task_id}")
    
    try:
        # Initialize parser
        parser = PerplexityParser()
        
        # Run the async process_insights in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def process_sections():
                async with AsyncSessionLocal() as session:
                    insight_repository = CommunityInsightRepository(session)
                    perplexity_client = PerplexityClient()
                    parser = PerplexityParser()
                    
                    # Process each section type independently
                    section_types = [
                        "Pain & Frustration Analysis",
                        "Failed Solutions Analysis",
                        "Question & Advice Mapping",
                        "Pattern Detection",
                        "Popular Products Analysis",
                        "Avatars"
                    ]
                    
                    all_sections = []
                    all_avatars = []
                    raw_response = ""
                    
                    for section_type in section_types:
                        try:
                            logger.info(f"Processing section: {section_type} with query: {user_query}")
                            
                            # Step 1: Generate insights from Perplexity
                            logger.info(f"Step 1: Generating insights for {section_type}")
                            section_content = await perplexity_client.generate_insights(
                                section_type=section_type,
                                topic_keyword=topic_keyword,
                                user_query=user_query,
                                source_urls=source_urls,
                                product_urls=product_urls,
                                use_only_specified_sources=use_only_specified_sources
                            )
                            
                            if not section_content or not section_content.get("raw_perplexity_response"):
                                logger.error(f"No content received for section {section_type}")
                                continue
                            
                            # Step 2: Parse the content
                            logger.info(f"Step 2: Parsing content for {section_type}")
                            parsed_content = await parser.process_section(
                                section_type=section_type,
                                content=section_content["raw_perplexity_response"],
                                topic_keyword=topic_keyword,
                                user_query=user_query
                            )
                            
                            # Step 3: Store the results
                            if parsed_content:
                                logger.info(f"Step 3: Storing results for {section_type}")
                                if parsed_content.get("section"):
                                    logger.info(f"Adding section: {parsed_content['section'].get('title')}")
                                    logger.info(f"Section insights: {json.dumps(parsed_content['section'].get('insights', []))}")
                                    all_sections.append(parsed_content["section"])
                                if parsed_content.get("avatars"):
                                    logger.info(f"Adding avatars: {len(parsed_content['avatars'])}")
                                    all_avatars.extend(parsed_content["avatars"])
                                raw_response += f"\n\n{section_content['raw_perplexity_response']}"
                            else:
                                logger.warning(f"No parsed content for section {section_type}")
                            
                        except Exception as e:
                            logger.error(f"Error processing section {section_type}: {str(e)}", exc_info=True)
                            continue
                    
                    # Step 4: Update the insight in the database
                    logger.info("Step 4: Updating insight in database")
                    logger.info(f"Sections to store: {json.dumps(all_sections)}")
                    logger.info(f"Avatars to store: {json.dumps(all_avatars)}")
                    
                    await insight_repository.append_to_insight(
                        task_id=self.request.id,
                        sections=all_sections,
                        avatars=all_avatars,
                        raw_response=raw_response.strip(),
                        status="completed"
                    )
                    
                    return {
                        "sections": all_sections,
                        "avatars": all_avatars,
                        "raw_perplexity_response": raw_response.strip()
                    }
            
            result = loop.run_until_complete(process_sections())
            
            return {
                "status": "completed",
                "sections": result["sections"],
                "avatars": result["avatars"],
                "raw_perplexity_response": result["raw_perplexity_response"]
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise InsightProcessingError(str(e)) 