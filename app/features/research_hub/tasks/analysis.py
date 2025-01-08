from typing import Optional, List, Dict, Any, Type
from celery import shared_task
import logging
from sqlalchemy import select
import asyncio
from app.core.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.features.research_hub.perplexity import get_client
from app.features.research_hub.repositories import create_repository
from app.features.research_hub.models.database.pain_analysis import PainAnalysis
from app.features.research_hub.models.database.question_analysis import QuestionAnalysis
from app.features.research_hub.models.database.pattern_analysis import PatternAnalysis
from app.features.research_hub.models.database.product_analysis import ProductAnalysis
from app.features.research_hub.models.database.avatar_analysis import AvatarAnalysis
from app.features.research_hub.websockets.analysis import notification_manager

logger = logging.getLogger(__name__)

# Mapping of analysis types to their model classes
ANALYSIS_TYPE_TO_MODEL = {
    "Pain & Frustration Analysis": PainAnalysis,
    "Question & Advice Mapping": QuestionAnalysis,
    "Pattern Detection": PatternAnalysis,
    "Popular Products Analysis": ProductAnalysis,
    "Avatars": AvatarAnalysis,
}

def run_async(coro):
    """Run an async function in a synchronous context."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(bind=True, max_retries=3)
def process_analysis(
    self,
    analysis_type: str,
    task_id: str,
    user_id: str,
    project_id: str,
    topic_keyword: str,
    user_query: str,
    source_urls: Optional[List[str]] = None,
    product_urls: Optional[List[str]] = None,
    use_only_specified_sources: bool = False
) -> Dict[str, Any]:
    """
    Process analysis asynchronously using Celery.
    """
    async def _process():
        try:
            logger.info(f"Starting {analysis_type} analysis for task {task_id}")
            
            # Get the appropriate model class
            model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
            
            # Notify start
            await notification_manager.notify_update(task_id, {
                "status": "processing",
                "message": "Starting analysis..."
            })
            
            # Get the appropriate client
            client = get_client(analysis_type)
            
            # Generate insights
            result = await client.generate_insights(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )
            
            if not result["structured_data"]:
                raise ValueError(f"Failed to generate {analysis_type} insights: No structured data returned")

            # Update database with results
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    # Get the analysis record
                    repository = create_repository(model_class)(session)
                    analysis = await repository.get_by_task_id(task_id, analysis_type)
                    
                    if not analysis:
                        raise ValueError(f"Analysis record not found for task {task_id}")
                    
                    # Update the record
                    analysis.status = "completed"
                    analysis.insights = result["structured_data"]
                    analysis.raw_perplexity_response = result["raw_perplexity_response"]
                
                logger.info(f"Successfully completed {analysis_type} analysis for task {task_id}")
                
                # Notify completion
                await notification_manager.notify_update(task_id, {
                    "status": "completed",
                    "insights": result["structured_data"]["insights"]
                })
                
                return {
                    "status": "completed",
                    "task_id": task_id,
                    "insights": result["structured_data"]["insights"]
                }

        except Exception as e:
            logger.error(f"Error processing {analysis_type} analysis for task {task_id}: {str(e)}", exc_info=True)
            
            try:
                # Update database with error
                async with AsyncSessionLocal() as session:
                    async with session.begin():
                        # Get the appropriate model class and repository
                        model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
                        repository = create_repository(model_class)(session)
                        analysis = await repository.get_by_task_id(task_id, analysis_type)
                        
                        if analysis:
                            analysis.status = "error"
                            analysis.error = str(e)
                
                # Notify error
                await notification_manager.notify_update(task_id, {
                    "status": "error",
                    "error": str(e)
                })
                
            except Exception as db_error:
                logger.error(f"Error updating database with error status: {str(db_error)}", exc_info=True)
            
            # Retry the task if appropriate
            if self.request.retries < self.max_retries:
                # Notify retry
                await notification_manager.notify_update(task_id, {
                    "status": "retrying",
                    "retry_count": self.request.retries + 1
                })
                raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))  # Exponential backoff
            
            raise

    return run_async(_process()) 