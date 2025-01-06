import asyncio
import logging
from typing import Dict, Any, List
from ....core.celery import celery_app as celery
from .task import CommunityInsightsTask
from .parser import PerplexityParser
from .repository import TaskRepository

logger = logging.getLogger(__name__)

@celery.task(bind=True, name="process_community_insights")
def process_community_insights(
    self,
    topic_keyword: str,
    user_query: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> Dict[str, Any]:
    """
    Process community insights for a given topic.
    """
    try:
        # Create task instance
        task_repository = TaskRepository()
        task = CommunityInsightsTask(
            parser=PerplexityParser(),
            task_repository=task_repository
        )
        
        # Create task in repository first
        task_id = self.request.id
        asyncio.run(task_repository.create_task(task_id))
        
        # Process insights
        result = asyncio.run(task.process_insights(
            task_id=task_id,
            topic_keyword=topic_keyword,
            user_query=user_query,
            source_urls=source_urls,
            product_urls=product_urls,
            use_only_specified_sources=use_only_specified_sources
        ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing community insights: {str(e)}", exc_info=True)
        # Return error result instead of raising to avoid task retry
        return {
            "status": "error",
            "sections": [],
            "avatars": [],
            "raw_perplexity_response": "",
            "error": str(e)
        } 