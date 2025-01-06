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
    get_avatars_prompt,
    get_product_analysis_prompt,
    get_failed_solutions_prompt
)
from ....core.config import settings
import json

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
            self.product_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            self.failed_solutions_client = AsyncOpenAI(
                api_key=settings.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )
            logger.info("CommunityInsightsTask initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CommunityInsightsTask: {str(e)}", exc_info=True)
            raise

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
            # Get or create insight for the project
            insight = await self.task_repository.get_or_create_insight(
                user_id=user_id,
                project_id=project_id,
                query=user_query
            )
            
            # Store task_id for subsequent updates
            task_id = insight.task_id
            logger.info(f"Working with task_id: {task_id}")

            # Get pain analysis from Perplexity
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
            logger.info("Successfully parsed pain analysis")
            logger.info(f"Pain Analysis Result:\n" + 
                     f"Title: {pain_result.title}\n" +
                     f"Icon: {pain_result.icon}\n" +
                     f"Number of insights: {len(pain_result.insights)}\n" +
                     f"Insights: {json.dumps([insight.dict() for insight in pain_result.insights], indent=2)}")
            
            # Update DB with pain analysis results
            logger.info("Updating database with pain analysis results")
            try:
                section_to_update = InsightSection(
                    title=pain_result.title,
                    icon=pain_result.icon,
                    insights=[{**insight.dict(), "query": user_query} for insight in pain_result.insights]
                ).dict()
                logger.info(f"Pain analysis section being sent to database: {json.dumps(section_to_update, indent=2)}")
                
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_sections=[section_to_update],
                    raw_response=f"Pain Analysis:\n{pain_content}"
                )
                logger.info("Successfully updated database with pain analysis")
            except Exception as e:
                logger.error(f"Failed to update database with pain analysis: {str(e)}", exc_info=True)
                raise

            # Get failed solutions from Perplexity
            logger.info("Calling Perplexity API for failed solutions")
            failed_solutions_prompt = get_failed_solutions_prompt(topic_keyword=topic_keyword)
            failed_solutions_response = await self.failed_solutions_client.chat.completions.create(
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
            logger.info(f"Failed Solutions Result:\n" + 
                     f"Title: {failed_solutions_result.title}\n" +
                     f"Icon: {failed_solutions_result.icon}\n" +
                     f"Number of insights: {len(failed_solutions_result.insights)}\n" +
                     f"Insights: {json.dumps([insight.dict() for insight in failed_solutions_result.insights], indent=2)}")
            
            # Update DB with failed solutions results
            logger.info("Updating database with failed solutions results")
            try:
                section_to_update = InsightSection(
                    title=failed_solutions_result.title,
                    icon=failed_solutions_result.icon,
                    insights=[{**insight.dict(), "query": user_query} for insight in failed_solutions_result.insights]
                ).dict()
                logger.info(f"Failed solutions section being sent to database: {json.dumps(section_to_update, indent=2)}")
                
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_sections=[section_to_update],
                    raw_response=f"Failed Solutions:\n{failed_solutions_content}"
                )
                logger.info("Successfully updated database with failed solutions")
            except Exception as e:
                logger.error(f"Failed to update database with failed solutions: {str(e)}", exc_info=True)
                raise

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
            logger.info("Successfully parsed question mapping")
            logger.info(f"Question Mapping Result:\n" + 
                     f"Title: {question_result.title}\n" +
                     f"Icon: {question_result.icon}\n" +
                     f"Number of insights: {len(question_result.insights)}\n" +
                     f"Insights: {json.dumps([insight.dict() for insight in question_result.insights], indent=2)}")
            
            # Update DB with question mapping results
            logger.info("Updating database with question mapping results")
            try:
                section_to_update = InsightSection(
                    title=question_result.title,
                    icon=question_result.icon,
                    insights=[{**insight.dict(), "query": user_query} for insight in question_result.insights]
                ).dict()
                logger.info(f"Question mapping section being sent to database: {json.dumps(section_to_update, indent=2)}")
                
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_sections=[section_to_update],
                    raw_response=f"Question Mapping:\n{question_content}"
                )
                logger.info("Successfully updated database with question mapping")
            except Exception as e:
                logger.error(f"Failed to update database with question mapping: {str(e)}", exc_info=True)
                raise

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
            logger.info("Successfully parsed pattern detection")
            logger.info(f"Pattern Detection Result:\n" + 
                     f"Title: {pattern_result.title}\n" +
                     f"Icon: {pattern_result.icon}\n" +
                     f"Number of insights: {len(pattern_result.insights)}\n" +
                     f"Insights: {json.dumps([insight.dict() for insight in pattern_result.insights], indent=2)}")
            
            # Update DB with pattern detection results
            logger.info("Updating database with pattern detection results")
            try:
                section_to_update = InsightSection(
                    title=pattern_result.title,
                    icon=pattern_result.icon,
                    insights=[{**insight.dict(), "query": user_query} for insight in pattern_result.insights]
                ).dict()
                logger.info(f"Pattern detection section being sent to database: {json.dumps(section_to_update, indent=2)}")
                
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_sections=[section_to_update],
                    raw_response=f"Pattern Detection:\n{pattern_content}"
                )
                logger.info("Successfully updated database with pattern detection")
            except Exception as e:
                logger.error(f"Failed to update database with pattern detection: {str(e)}", exc_info=True)
                raise

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
            logger.info("Successfully parsed avatars")
            logger.info(f"Avatars Result:\n" + 
                     f"Number of avatars: {len(avatars_result.avatars)}\n" +
                     f"Avatars: {json.dumps([avatar.dict() for avatar in avatars_result.avatars], indent=2)}")

            # Update DB with avatars results
            logger.info("Updating database with avatars results")
            try:
                # Format avatars data
                formatted_avatars = []
                for avatar in avatars_result.avatars:
                    # Convert avatar to dict and validate
                    avatar_dict = avatar.dict()
                    formatted_avatar = {
                        "name": str(avatar_dict["name"]),
                        "type": str(avatar_dict["type"]),
                        "insights": []
                    }
                    
                    # Process each insight
                    for insight in avatar_dict["insights"]:
                        formatted_insight = {
                            "title": str(insight.get("title", "")),
                            "description": str(insight.get("description", "")),
                            "evidence": str(insight.get("evidence", "")),
                            "query": str(user_query),
                            "needs": list(insight.get("needs", [])) if isinstance(insight.get("needs"), list) else [],
                            "pain_points": list(insight.get("pain_points", [])) if isinstance(insight.get("pain_points"), list) else [],
                            "behaviors": list(insight.get("behaviors", [])) if isinstance(insight.get("behaviors"), list) else []
                        }
                        formatted_avatar["insights"].append(formatted_insight)

                    formatted_avatars.append(formatted_avatar)

                logger.info(f"Formatted avatars for database: {json.dumps(formatted_avatars, indent=2)}")
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_avatars=formatted_avatars,
                    raw_response=f"Avatars:\n{avatars_content}"
                )
                logger.info("Successfully updated database with avatars")
            except Exception as e:
                logger.error(f"Failed to update database with avatars: {str(e)}", exc_info=True)
                raise

            # Get product analysis from Perplexity
            logger.info("Calling Perplexity API for product analysis")
            product_prompt = get_product_analysis_prompt(topic_keyword=topic_keyword)
            product_response = await self.product_client.chat.completions.create(
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
            logger.info(f"Product Analysis Result:\n" + 
                     f"Title: {product_result.title}\n" +
                     f"Icon: {product_result.icon}\n" +
                     f"Number of insights: {len(product_result.insights)}\n" +
                     f"Insights: {json.dumps([insight.dict() for insight in product_result.insights], indent=2)}")
            
            # Update DB with product analysis results
            logger.info("Updating database with product analysis results")
            try:
                section_to_update = InsightSection(
                    title=product_result.title,
                    icon=product_result.icon,
                    insights=[{**insight.dict(), "query": user_query} for insight in product_result.insights]
                ).dict()
                logger.info(f"Product analysis section being sent to database: {json.dumps(section_to_update, indent=2)}")
                
                await self.task_repository.append_to_insight(
                    task_id=task_id,
                    new_sections=[section_to_update],
                    raw_response=f"Product Analysis:\n{product_content}"
                )
                logger.info("Successfully updated database with product analysis")
            except Exception as e:
                logger.error(f"Failed to update database with product analysis: {str(e)}", exc_info=True)
                raise

            # Return the final insight
            logger.info(f"Retrieving final insight for task {task_id}")
            final_insight = await self.task_repository.get_task_insight(task_id)
            if not final_insight:
                logger.error(f"Failed to retrieve final insight for task {task_id}")
                raise ValueError(f"No insight found for task {task_id}")
                
            return {
                "status": "completed",
                "task_id": task_id,
                "sections": final_insight.sections,
                "avatars": final_insight.avatars,
                "raw_perplexity_response": final_insight.raw_perplexity_response
            }

        except Exception as e:
            logger.error(f"Error processing insights: {str(e)}", exc_info=True)
            # Update insight with error
            try:
                await self.task_repository.append_to_insight(
                    project_id,
                    error=str(e)
                )
            except Exception as update_error:
                logger.error(f"Failed to update insight with error: {str(update_error)}", exc_info=True)
            raise