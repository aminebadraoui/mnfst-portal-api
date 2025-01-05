from typing import Dict, Any
from ....core.celery import celery_app
from .task import CommunityInsightsTask
from .parser import PerplexityParser
from .repository import TaskRepository
import logging
import asyncio

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_community_insights")
def process_community_insights(self,
    topic_keyword: str,
    source_urls: list = None,
    product_urls: list = None,
    use_only_specified_sources: bool = False
) -> Dict[str, Any]:
    """
    Celery task to process community insights.
    """
    try:
        logger.info("Starting community insights processing")
        task_id = self.request.id
        logger.info(f"Processing task {task_id}")
        
        # Initialize dependencies
        parser = PerplexityParser()
        repository = TaskRepository()
        task = CommunityInsightsTask(parser=parser, task_repository=repository)
        
        # Create task in repository
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repository.create_task(task_id))
        
        # Run the async task in the event loop
        return loop.run_until_complete(task.process_insights(
            task_id=task_id,
            topic_keyword=topic_keyword,
            source_urls=source_urls,
            product_urls=product_urls,
            use_only_specified_sources=use_only_specified_sources
        ))
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "sections": [],
            "avatars": [],
            "raw_perplexity_response": "",
            "error": str(e)
        } 