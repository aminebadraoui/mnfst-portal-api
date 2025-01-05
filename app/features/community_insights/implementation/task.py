from typing import Dict, List, Optional, Any
import logging
from openai import AsyncOpenAI
from .task_model import Task
from .task_status import TaskStatus
from .parser import PerplexityParser
from .repository import TaskRepository
from .base_models import InsightSection, Avatar, AvatarInsight, ParserResult
from ..prompts.templates import (
    get_pain_analysis_prompt,
    get_question_mapping_prompt,
    get_pattern_detection_prompt,
    get_avatars_prompt
)
from ....core.config import settings

logger = logging.getLogger(__name__)

class CommunityInsightsTask:
    def __init__(self, parser: PerplexityParser, task_repository: TaskRepository):
        try:
            logger.info("Initializing CommunityInsightsTask")
            self.parser = parser
            self.task_repository = task_repository
            
            # Initialize separate clients for each section
            self.pain_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            self.question_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            self.pattern_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            self.avatars_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            logger.info("CommunityInsightsTask initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CommunityInsightsTask: {str(e)}", exc_info=True)
            raise

    async def process_insights(
        self,
        task_id: str,
        topic_keyword: str,
        source_urls: list = None,
        product_urls: list = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Process the insights for a given task.
        """
        try:
            logger.info(f"Processing insights for task {task_id}")
            logger.debug(f"Topic keyword: {topic_keyword}")

            try:
                # Get pain & frustration analysis from Perplexity
                logger.info("Calling Perplexity API for pain analysis")
                pain_prompt = get_pain_analysis_prompt(topic_keyword=topic_keyword)
                pain_response = await self.pain_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{
                        "role": "user",
                        "content": pain_prompt
                    }]
                )
                pain_content = pain_response.choices[0].message.content
                logger.debug(f"Received pain analysis from Perplexity (first 500 chars): {pain_content[:500]}")
                
                # Parse pain analysis immediately
                pain_result = await self.parser.parse_pain_analysis(pain_content, topic_keyword)
                logger.debug(f"Parsed pain analysis: {pain_result}")

                # Get question & advice mapping from Perplexity
                logger.info("Calling Perplexity API for question mapping")
                question_prompt = get_question_mapping_prompt(topic_keyword=topic_keyword)
                question_response = await self.question_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{
                        "role": "user",
                        "content": question_prompt
                    }]
                )
                question_content = question_response.choices[0].message.content
                logger.debug(f"Received question mapping from Perplexity (first 500 chars): {question_content[:500]}")
                
                # Parse question mapping immediately
                question_result = await self.parser.parse_question_mapping(question_content, topic_keyword)
                logger.debug(f"Parsed question mapping: {question_result}")

                # Get pattern detection from Perplexity
                logger.info("Calling Perplexity API for pattern detection")
                pattern_prompt = get_pattern_detection_prompt(topic_keyword=topic_keyword)
                pattern_response = await self.pattern_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{
                        "role": "user",
                        "content": pattern_prompt
                    }]
                )
                pattern_content = pattern_response.choices[0].message.content
                logger.debug(f"Received pattern detection from Perplexity (first 500 chars): {pattern_content[:500]}")
                
                # Parse pattern detection immediately
                pattern_result = await self.parser.parse_pattern_detection(pattern_content, topic_keyword)
                logger.debug(f"Parsed pattern detection: {pattern_result}")

                # Get avatars from Perplexity
                logger.info("Calling Perplexity API for avatars")
                avatars_prompt = get_avatars_prompt(topic_keyword=topic_keyword)
                avatars_response = await self.avatars_client.chat.completions.create(
                    model="llama-3.1-sonar-small-128k-online",
                    messages=[{
                        "role": "user",
                        "content": avatars_prompt
                    }]
                )
                avatars_content = avatars_response.choices[0].message.content
                logger.debug(f"Received avatars from Perplexity (first 500 chars): {avatars_content[:500]}")
                
                # Parse avatars immediately
                avatars_result = await self.parser.parse_avatars(avatars_content, topic_keyword)
                logger.debug(f"Parsed avatars: {avatars_result}")

                # Combine all results
                sections = [
                    InsightSection(
                        title=pain_result.title,
                        icon=pain_result.icon,
                        insights=[insight.dict() for insight in pain_result.insights]
                    ),
                    InsightSection(
                        title=question_result.title,
                        icon=question_result.icon,
                        insights=[insight.dict() for insight in question_result.insights]
                    ),
                    InsightSection(
                        title=pattern_result.title,
                        icon=pattern_result.icon,
                        insights=[insight.dict() for insight in pattern_result.insights]
                    )
                ]

                # Convert avatars to the right format
                avatars = [
                    Avatar(
                        name=avatar.name,
                        type=avatar.type,
                        insights=[
                            AvatarInsight(
                                title=insight.title,
                                description=insight.description,
                                evidence=insight.evidence,
                                needs=insight.needs,
                                pain_points=insight.pain_points,
                                behaviors=insight.behaviors
                            ) for insight in avatar.insights
                        ]
                    ) for avatar in avatars_result.avatars
                ]

                # Create final result
                parser_result = {
                    "status": "completed",
                    "sections": [section.dict() for section in sections],
                    "avatars": [avatar.dict() for avatar in avatars],
                    "raw_perplexity_response": f"""Pain Analysis:
{pain_content}

Question Mapping:
{question_content}

Pattern Detection:
{pattern_content}

Avatars:
{avatars_content}"""
                }

                # Update task with results
                logger.info("Updating task with parser results")
                await self.task_repository.update_task(
                    task_id,
                    status="completed",
                    sections=parser_result["sections"],
                    avatars=parser_result["avatars"],
                    raw_response=parser_result["raw_perplexity_response"]
                )
                logger.info(f"Task {task_id} completed successfully")
                
                return parser_result

            except Exception as e:
                logger.error(f"Error during processing: {str(e)}", exc_info=True)
                error_result = {
                    "status": "error",
                    "sections": [],
                    "avatars": [],
                    "raw_perplexity_response": "",
                    "error": str(e)
                }
                await self.task_repository.update_task(
                    task_id,
                    status="error",
                    error=f"Processing error: {str(e)}",
                    raw_response=getattr(e, 'raw_response', None)
                )
                return error_result

        except Exception as e:
            logger.error(f"Error processing insights for task {task_id}: {str(e)}", exc_info=True)
            try:
                error_result = {
                    "status": "error",
                    "sections": [],
                    "avatars": [],
                    "raw_perplexity_response": "",
                    "error": str(e)
                }
                await self.task_repository.update_task(
                    task_id,
                    status="error",
                    error=f"Processing error: {str(e)}",
                    raw_response=getattr(e, 'raw_response', None)
                )
                return error_result
            except Exception as update_error:
                logger.error(f"Error updating task status: {str(update_error)}", exc_info=True)
                return {
                    "status": "error",
                    "sections": [],
                    "avatars": [],
                    "raw_perplexity_response": "",
                    "error": f"Error updating task status: {str(update_error)}"
                }