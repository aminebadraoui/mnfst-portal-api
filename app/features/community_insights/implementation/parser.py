from typing import List
from pydantic import BaseModel, Field
import logging
import json
import re
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ....core.config import settings
from .models import InsightItem, InsightSection, CommunityInsightsResponse

logger = logging.getLogger(__name__)

class ParserInput(BaseModel):
    content: str
    topic_keyword: str

class PerplexityParser:
    def __init__(self):
        logger.info("Initializing PerplexityParser")
        try:
            self.model = OpenAIModel('gpt-4o-mini')
            logger.info("OpenAI model initialized with gpt-4o-mini")
            
            self.agent = Agent(
                model=self.model,
                system_prompt="""You are a data parser specialized in extracting structured insights from text.
                Your task is to parse the given text into EXACTLY THREE sections of insights.
                Each section should contain a list of insights.
                
                Use ONLY these three sections with their corresponding icons:
                1. Pain & Frustration Analysis (icon: FaExclamationCircle)
                2. Question & Advice Mapping (icon: FaQuestionCircle)
                3. Pattern Detection (icon: FaChartLine)
                
                Your response must be a valid JSON object with this structure:
                {
                    "status": "completed",
                    "sections": [
                        {
                            "title": "Pain & Frustration Analysis",
                            "icon": "FaExclamationCircle",
                            "insights": [
                                {
                                    "title": "Title of the insight",
                                    "evidence": "Direct quote from the text",
                                    "source_url": "URL where the evidence was found",
                                    "engagement_metrics": "e.g., 500 upvotes, 200 comments",
                                    "frequency": "e.g., Common in discussions about...",
                                    "correlation": "e.g., Often linked to...",
                                    "significance": "e.g., Highlights the importance of..."
                                }
                            ]
                        }
                    ]
                }
                
                For each insight, you must include:
                - A clear title
                - Supporting evidence (direct quotes)
                - Source URL
                - Engagement metrics (e.g., upvotes, comments)
                - Frequency of occurrence
                - Correlation with other patterns
                - Significance/implications
                
                Counter-intuitive insights should be distributed within the three sections based on their type.
                
                IMPORTANT:
                - You MUST output valid JSON
                - You MUST include all three sections
                - Each section MUST have the exact title and icon specified above
                - Each insight MUST have all the required fields"""
            )
            logger.info("Pydantic AI agent initialized with system prompt")
        except Exception as e:
            logger.error(f"Error initializing PerplexityParser: {str(e)}", exc_info=True)
            raise

    async def parse_response(self, content: str, topic_keyword: str) -> CommunityInsightsResponse:
        """
        Use GPT-4o-mini to parse the Perplexity response into structured data.
        """
        try:
            logger.info(f"Starting to parse response for topic: {topic_keyword}")
            logger.debug(f"Content length to parse: {len(content)} characters")
            
            # Create parser input
            parser_input = ParserInput(
                content=content,
                topic_keyword=topic_keyword
            )
            logger.debug(f"Created parser input: {parser_input.model_dump_json()}")
            
            # Run parser
            logger.info("Running GPT-4o-mini parser")
            try:
                prompt = f"""Parse the following text into structured sections and insights.
                You MUST output a valid JSON object with EXACTLY three sections:
                1. Pain & Frustration Analysis (icon: FaExclamationCircle)
                2. Question & Advice Mapping (icon: FaQuestionCircle)
                3. Pattern Detection (icon: FaChartLine)
                
                Each section MUST have:
                - The exact title as specified above
                - The exact icon name as specified above
                - A list of insights
                
                Each insight MUST have:
                - title: A descriptive title
                - evidence: A direct quote from the text
                - source_url: The URL where the evidence was found
                - engagement_metrics: Engagement data (e.g., upvotes and comments)
                - frequency: How frequently this appears
                - correlation: What it's linked to
                - significance: Why it's significant
                
                Topic keyword to use: {topic_keyword}
                
                Text to parse:
                {content}
                
                Remember: Your response MUST be valid JSON with the exact structure specified in the system prompt."""
                
                result = await self.agent.run(prompt)
                logger.debug(f"Raw parser response type: {type(result)}")
                logger.debug(f"Raw parser response: {result}")
                
                # Handle the raw response first
                if result is None:
                    logger.warning("Received None response from agent")
                    return CommunityInsightsResponse(status="completed", sections=[])
                
                try:
                    # Try to get the data attribute
                    response_data = getattr(result, 'data', None)
                    logger.debug(f"Raw parser response data type: {type(response_data)}")
                    logger.debug(f"Raw parser response data: {response_data}")
                    
                    if response_data is None:
                        logger.warning("Response data is None")
                        return CommunityInsightsResponse(status="completed", sections=[])
                    
                    # Convert the response to our model format
                    if isinstance(response_data, str):
                        try:
                            # Try to parse as JSON if it looks like JSON
                            if response_data.strip().startswith('{'):
                                response_dict = json.loads(response_data)
                            else:
                                # Try to extract JSON from the text
                                json_match = re.search(r'\{.*\}', response_data, re.DOTALL)
                                if json_match:
                                    response_dict = json.loads(json_match.group(0))
                                else:
                                    logger.warning(f"Could not find JSON in response: {response_data[:100]}...")
                                    return CommunityInsightsResponse(status="completed", sections=[])
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON response: {str(e)}")
                            return CommunityInsightsResponse(status="completed", sections=[])
                    else:
                        response_dict = response_data
                    
                    logger.debug(f"Response dict before validation: {response_dict}")
                    
                    # Ensure we have a dictionary
                    if not isinstance(response_dict, dict):
                        logger.warning(f"Response is not a dict, got {type(response_dict)}")
                        response_dict = {"status": "completed", "sections": []}
                    
                    # Ensure required fields
                    response_dict.setdefault("status", "completed")
                    response_dict.setdefault("sections", [])
                    
                    # Validate with our model
                    parsed_data = CommunityInsightsResponse.model_validate(response_dict)
                    
                    if len(parsed_data.sections) > 0:
                        logger.info(f"Successfully parsed response into {len(parsed_data.sections)} sections")
                        logger.debug(f"Parsed sections: {[section.title for section in parsed_data.sections]}")

                        # Log detailed section information
                        for section in parsed_data.sections:
                            logger.debug(f"Section '{section.title}' contains {len(section.insights)} insights")
                            for i, insight in enumerate(section.insights):
                                logger.debug(f"  Insight {i+1}: {insight.title}")
                    else:
                        logger.warning("No sections were parsed from the response")
                    
                    return parsed_data
                    
                except Exception as e:
                    logger.error(f"Error during response processing: {str(e)}", exc_info=True)
                    return CommunityInsightsResponse(status="completed", sections=[])
                    
            except Exception as e:
                logger.error(f"Error during GPT-4o-mini parsing: {str(e)}", exc_info=True)
                raise

        except Exception as e:
            logger.error(f"Error in parse_response: {str(e)}", exc_info=True)
            raise 