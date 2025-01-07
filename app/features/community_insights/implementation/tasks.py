from typing import Dict, List, Optional, Any
import logging
from celery import shared_task
from .task import CommunityInsightsTask
from .parser import PerplexityParser
from .repository import TaskRepository, CommunityInsightRepository
from ....core.config import settings
from ....core.celery import celery_app
from ....core.database import AsyncSessionLocal
import asyncio
import json
import traceback
from celery.exceptions import TaskError

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
    """
    logger.info(f"Starting process_insights_task for project {project_id}")
    try:
        # Update task state to STARTED
        self.update_state(state='STARTED', meta={'message': 'Task started'})
        
        # Initialize parser and repository
        parser = PerplexityParser()
        insight_repository = CommunityInsightRepository(None)  # Will be initialized with session later
        task_repository = TaskRepository(None)  # Will be initialized with session later
        
        # Run the async process_insights in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run process_insights and update status in the same event loop
            async def process_and_update():
                try:
                    # Create repository with database session
                    async with AsyncSessionLocal() as session:
                        insight_repository.session = session  # Set the session
                        task_repository.session = session  # Set the session
                        task = CommunityInsightsTask(parser=parser, task_repository=insight_repository)
                        
                        result = await task.process_insights(
                            project_id=project_id,
                            user_id=user_id,
                            topic_keyword=topic_keyword,
                            user_query=user_query,
                            source_urls=source_urls,
                            product_urls=product_urls,
                            use_only_specified_sources=use_only_specified_sources,
                            task_id=self.request.id  # Pass the Celery task ID
                        )
                        
                        logger.info("Parsed results received from task:")
                        logger.info(f"Number of sections: {len(result.get('sections', []))}")
                        logger.info(f"Number of avatars: {len(result.get('avatars', []))}")
                        
                        # Save the results using the repository
                        logger.info("Attempting to save results to database")
                        try:
                            # Get the task_id from the result
                            task_id = result.get('task_id')
                            if not task_id:
                                raise ValueError("No task_id found in result")
                                
                            logger.info(f"Attempting to save sections for task {task_id}")
                            logger.info(f"Sections to save: {json.dumps(result.get('sections', []), indent=2)}")
                            
                            # Update the insight with all data
                            sections = result.get("sections", [])
                            if not isinstance(sections, list):
                                logger.error(f"Invalid sections format - expected list but got {type(sections)}")
                                sections = []
                            
                            avatars = result.get("avatars", [])
                            if not isinstance(avatars, list):
                                logger.error(f"Invalid avatars format - expected list but got {type(avatars)}")
                                avatars = []
                                
                            await insight_repository.append_to_insight(
                                task_id=task_id,
                                new_sections=sections,
                                new_avatars=avatars,
                                raw_response=result.get("raw_perplexity_response", "")
                            )
                            
                            # Verify the save was successful by reading back the data
                            saved_insight = await insight_repository.get_task_insight(task_id)
                            if not saved_insight:
                                raise ValueError(f"Failed to verify save - could not find task {task_id}")
                            
                            if not saved_insight.sections:
                                raise ValueError(f"Failed to verify save - no sections found for task {task_id}")
                                
                            logger.info(f"Successfully verified save - found {len(saved_insight.sections)} sections in database")
                            logger.info(f"Saved sections: {json.dumps(saved_insight.sections, indent=2)}")
                            
                            # Update task status to completed as the final step
                            await task_repository.update_task_status(task_id, "completed")
                            logger.info(f"Task completed successfully for project {project_id}")
                            
                        except Exception as save_error:
                            logger.error(f"Failed to save results: {str(save_error)}", exc_info=True)
                            raise
                        
                        return result
                except Exception as inner_e:
                    logger.error(f"Error in async process: {str(inner_e)}", exc_info=True)
                    # Update task with error
                    try:
                        await insight_repository.append_to_insight(
                            task_id=task_id,
                            error=str(inner_e)
                        )
                    except Exception as update_e:
                        logger.error(f"Failed to update task with error: {str(update_e)}", exc_info=True)
                    raise InsightProcessingError(f"Failed to process insights: {str(inner_e)}")

            result = loop.run_until_complete(process_and_update())
            
            return {
                "status": "completed",
                "sections": result.get("sections", []),
                "avatars": result.get("avatars", []),
                "raw_perplexity_response": result.get("raw_perplexity_response")
            }
        finally:
            loop.close()
    except Exception as e:
        error_details = {
            'exc_type': type(e).__name__,
            'exc_message': str(e),
            'exc_traceback': traceback.format_exc()
        }
        logger.error(f"Error in process_insights_task: {error_details}", exc_info=True)
        # Update task state to FAILURE with proper error details
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                'exc_traceback': traceback.format_exc()
            }
        )
        raise InsightProcessingError(str(e)).with_traceback(e.__traceback__) 