from typing import Dict, List, Optional, Any
import logging
from celery import shared_task
from openai import OpenAI
from .task_model import Task
from .task_status import TaskStatus
from .parser import PerplexityParser
from .repository import CommunityInsightRepository
from .base_models import InsightSection, Avatar, AvatarInsight, ParserResult
from ..prompts.templates import (
    get_pain_analysis_prompt,
    get_question_mapping_prompt,
    get_pattern_detection_prompt,
    get_avatars_prompt,
    get_product_analysis_prompt,
    get_failed_solutions_prompt
)
from ....core.config import settings
from ....core.celery import celery_app
from ....core.database import AsyncSessionLocal
import asyncio

logger = logging.getLogger(__name__)

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
        
        task = CommunityInsightsTask()
        # Run the async process_insights in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(task.process_insights(
                project_id=project_id,
                user_id=user_id,
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            ))
            logger.info(f"Task completed successfully for project {project_id}")
            return {
                "status": "completed",
                "sections": result.get("sections", []),
                "avatars": result.get("avatars", []),
                "raw_perplexity_response": result.get("raw_perplexity_response")
            }
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in process_insights_task: {str(e)}", exc_info=True)
        # Update task state to FAILURE
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

class CommunityInsightsTask:
    def __init__(self):
        logger.info("Initializing CommunityInsightsTask")
        self.parser = PerplexityParser()
        
        # Initialize separate clients for each section
        self.pain_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        self.question_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        self.pattern_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        self.avatars_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        self.product_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        self.failed_solutions_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        logger.info("CommunityInsightsTask initialized successfully")

    async def process_insights(
        self,
        project_id: str,
        user_id: str,
        topic_keyword: str,
        user_query: str,
        source_urls: list = None,
        product_urls: list = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Process insights for a project."""
        logger.info(f"Processing insights for project {project_id}")
        try:
            # Get pain analysis from Perplexity
            logger.info("Calling Perplexity API for pain analysis")
            pain_prompt = get_pain_analysis_prompt(topic_keyword=topic_keyword)
            pain_response = self.pain_client.chat.completions.create(
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
            logger.info("Successfully parsed pain analysis")
            logger.debug(f"Pain analysis result: {pain_result}")
            
            # Store pain analysis results
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_sections=[InsightSection(
                        title=pain_result.title,
                        icon=pain_result.icon,
                        insights=[{**insight.dict(), "query": user_query} for insight in pain_result.insights]
                    ).dict()],
                    raw_response=f"Pain Analysis:\n{pain_content}"
                )

            # Get failed solutions from Perplexity
            logger.info("Calling Perplexity API for failed solutions")
            failed_solutions_prompt = get_failed_solutions_prompt(topic_keyword=topic_keyword)
            failed_solutions_response = self.failed_solutions_client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{
                    "role": "user",
                    "content": failed_solutions_prompt
                }]
            )
            failed_solutions_content = failed_solutions_response.choices[0].message.content
            logger.debug(f"Received failed solutions from Perplexity (first 500 chars): {failed_solutions_content[:500]}")
            
            # Parse failed solutions immediately
            failed_solutions_result = await self.parser.parse_failed_solutions(failed_solutions_content, topic_keyword)
            logger.info("Successfully parsed failed solutions")
            logger.debug(f"Failed solutions result: {failed_solutions_result}")
            
            # Store failed solutions results
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_sections=[InsightSection(
                        title=failed_solutions_result.title,
                        icon=failed_solutions_result.icon,
                        insights=[{**insight.dict(), "query": user_query} for insight in failed_solutions_result.insights]
                    ).dict()],
                    raw_response=f"Failed Solutions:\n{failed_solutions_content}"
                )

            # Get question & advice mapping from Perplexity
            logger.info("Calling Perplexity API for question mapping")
            question_prompt = get_question_mapping_prompt(topic_keyword=topic_keyword)
            question_response = self.question_client.chat.completions.create(
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
            logger.info("Successfully parsed question mapping")
            logger.debug(f"Question mapping result: {question_result}")
            
            # Store question mapping results
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_sections=[InsightSection(
                        title=question_result.title,
                        icon=question_result.icon,
                        insights=[{**insight.dict(), "query": user_query} for insight in question_result.insights]
                    ).dict()],
                    raw_response=f"Question Mapping:\n{question_content}"
                )

            # Get pattern detection from Perplexity
            logger.info("Calling Perplexity API for pattern detection")
            pattern_prompt = get_pattern_detection_prompt(topic_keyword=topic_keyword)
            pattern_response = self.pattern_client.chat.completions.create(
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
            logger.info("Successfully parsed pattern detection")
            logger.debug(f"Pattern detection result: {pattern_result}")
            
            # Store pattern detection results
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_sections=[InsightSection(
                        title=pattern_result.title,
                        icon=pattern_result.icon,
                        insights=[{**insight.dict(), "query": user_query} for insight in pattern_result.insights]
                    ).dict()],
                    raw_response=f"Pattern Detection:\n{pattern_content}"
                )

            # Get avatars from Perplexity
            logger.info("Calling Perplexity API for avatars")
            avatars_prompt = get_avatars_prompt(topic_keyword=topic_keyword)
            avatars_response = self.avatars_client.chat.completions.create(
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
            logger.info("Successfully parsed avatars")
            logger.debug(f"Avatars result: {avatars_result}")
            
            # Store avatars results
            avatars = [
                Avatar(
                    name=avatar.name,
                    type=avatar.type,
                    insights=[
                        AvatarInsight(
                            title=insight.title,
                            description=insight.description,
                            evidence=insight.evidence,
                            query=user_query,
                            needs=insight.needs,
                            pain_points=insight.pain_points,
                            behaviors=insight.behaviors
                        ) for insight in avatar.insights
                    ]
                ) for avatar in avatars_result.avatars
            ]
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_avatars=[avatar.dict() for avatar in avatars],
                    raw_response=f"Avatars:\n{avatars_content}"
                )

            # Get product analysis from Perplexity
            logger.info("Calling Perplexity API for product analysis")
            product_prompt = get_product_analysis_prompt(topic_keyword=topic_keyword)
            product_response = self.product_client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{
                    "role": "user",
                    "content": product_prompt
                }]
            )
            product_content = product_response.choices[0].message.content
            logger.debug(f"Received product analysis from Perplexity (first 500 chars): {product_content[:500]}")
            
            # Parse product analysis immediately
            product_result = await self.parser.parse_product_analysis(product_content, topic_keyword)
            logger.info("Successfully parsed product analysis")
            logger.debug(f"Product analysis result: {product_result}")
            
            # Store product analysis results
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                await repository.append_to_insight(
                    project_id,
                    new_sections=[InsightSection(
                        title=product_result.title,
                        icon=product_result.icon,
                        insights=[{**insight.dict(), "query": user_query} for insight in product_result.insights]
                    ).dict()],
                    raw_response=f"Product Analysis:\n{product_content}"
                )

            # Get final insight
            async with AsyncSessionLocal() as session:
                repository = CommunityInsightRepository(session)
                final_insight = await repository.get_project_insight(project_id)
                return {
                    "status": "completed",
                    "sections": final_insight.sections,
                    "avatars": final_insight.avatars,
                    "raw_perplexity_response": final_insight.raw_perplexity_response
                }

        except Exception as e:
            logger.error(f"Error processing insights: {str(e)}", exc_info=True)
            # Update insight with error
            try:
                async with AsyncSessionLocal() as session:
                    repository = CommunityInsightRepository(session)
                    await repository.append_to_insight(
                        project_id,
                        error=str(e)
                    )
            except Exception as update_error:
                logger.error(f"Failed to update insight with error: {str(update_error)}", exc_info=True)
            raise 