from typing import Dict, List, Optional, Any
import logging
from .base import BasePerplexityClient
from ..prompts.templates import get_prompt, AnalysisType
from ..parsers import QuestionParser

logger = logging.getLogger(__name__)

class QuestionPerplexityClient(BasePerplexityClient):
    """Client for question & advice mapping using Perplexity API."""
    
    def __init__(self):
        super().__init__()
        self.parser = QuestionParser()

    async def generate_insights(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate question & advice mapping insights using Perplexity."""
        try:
            # Get prompt
            prompt = get_prompt(
                analysis_type=AnalysisType.QUESTION,
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )

            # Make API request
            raw_response = await self._make_request(prompt)
            if not raw_response:
                logger.error("No response received from Perplexity API")
                return {
                    "raw_perplexity_response": "",
                    "structured_data": None
                }

            # Log the raw response for debugging
            logger.debug(f"Raw Perplexity response: {raw_response}")

            # Process the response to structure it better
            processed_response = self._process_response(raw_response)
            
            # Parse the processed response
            parsed_data = await self.parser.parse(processed_response, topic_keyword=topic_keyword, user_query=user_query)
            
            # Convert to dict and ensure insights are present
            result = parsed_data.dict()
            if not result.get("insights"):
                logger.warning("No insights found in parsed data")
                return {
                    "raw_perplexity_response": raw_response,
                    "structured_data": {"insights": []}
                }

            logger.info(f"Successfully parsed {len(result['insights'])} insights")
            return {
                "raw_perplexity_response": raw_response,
                "structured_data": result
            }

        except Exception as e:
            logger.error(f"Error generating question mapping insights: {str(e)}", exc_info=True)
            return {
                "raw_perplexity_response": "",
                "structured_data": None
            }

    def _process_response(self, response: str) -> str:
        """Process the raw Perplexity response into a structured format string."""
        try:
            # Split response into sections based on titles/patterns
            sections = response.split("\n\n")
            
            # Build structured response
            structured_sections = []
            current_section = []
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Start a new section when we see a title-like line
                if section.isupper() or section.startswith("#") or section.startswith("Title:"):
                    if current_section:
                        structured_sections.append("\n".join(current_section))
                    current_section = [section]
                    continue
                
                # Process section based on content
                lower_section = section.lower()
                if any(marker in lower_section for marker in [
                    "question type:", "evidence:", "quote:", 
                    "solution:", "answer:", "related question",
                    "engagement:", "metric:"
                ]):
                    current_section.append(section)
            
            # Add the last section
            if current_section:
                structured_sections.append("\n".join(current_section))
            
            # Combine all sections with clear separation
            processed_response = "\n\n---\n\n".join(structured_sections)
            
            # If no structured content, return original
            if not processed_response:
                return response
                
            return processed_response
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}", exc_info=True)
            return response 