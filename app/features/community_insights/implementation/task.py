from typing import Dict, List, Optional, Any
import logging
from openai import AsyncOpenAI
from .task_model import Task
from .task_status import TaskStatus
from .parser import PerplexityParser
from .repository import TaskRepository
from ....core.config import settings

logger = logging.getLogger(__name__)

class CommunityInsightsTask:
    def __init__(self, parser: PerplexityParser, task_repository: TaskRepository):
        try:
            logger.info("Initializing CommunityInsightsTask")
            self.parser = parser
            self.task_repository = task_repository
            self.perplexity_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            logger.info("CommunityInsightsTask initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CommunityInsightsTask: {str(e)}", exc_info=True)
            raise

    async def process_insights(self, task_id: str, content: str, topic_keyword: str) -> None:
        """
        Process the insights for a given task.
        """
        try:
            logger.info(f"Processing insights for task {task_id}")
            logger.debug(f"Topic keyword: {topic_keyword}")

            try:
                # Get content from Perplexity
                logger.info("Calling Perplexity API")
                perplexity_response = await self.perplexity_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{
                        "role": "user",
                        "content": f"Analyze online discussions about {topic_keyword}. Focus on user needs, pain points, and behaviors."
                    }]
                )
                content = perplexity_response.choices[0].message.content
                logger.debug(f"Received response from Perplexity (first 500 chars): {content[:500]}")

                # Parse the response
                logger.info("Starting parser")
                parser_result = await self.parser.parse_response(content, topic_keyword)
                logger.debug(f"Parser result: {parser_result}")

                # Update task with results
                logger.info("Updating task with parser results")
                await self.task_repository.update_task(
                    task_id,
                    status=TaskStatus.COMPLETED,
                    sections=parser_result.sections,
                    avatars=parser_result.avatars,
                    raw_response=parser_result.raw_perplexity_response
                )
                logger.info(f"Task {task_id} completed successfully")

            except Exception as e:
                logger.error(f"Error during processing: {str(e)}", exc_info=True)
                await self.task_repository.update_task(
                    task_id,
                    status=TaskStatus.ERROR,
                    error=f"Processing error: {str(e)}",
                    raw_response=getattr(e, 'raw_response', None)
                )
                raise

        except Exception as e:
            logger.error(f"Error processing insights for task {task_id}: {str(e)}", exc_info=True)
            try:
                await self.task_repository.update_task(
                    task_id,
                    status=TaskStatus.ERROR,
                    error=str(e),
                    raw_response=getattr(e, 'raw_response', None)
                )
            except Exception as update_error:
                logger.error(f"Error updating task status: {str(update_error)}", exc_info=True)
            raise