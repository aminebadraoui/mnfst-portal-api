from typing import Dict, List, Optional, Any
import logging
from .base import BasePerplexityClient
from ..prompts.templates import get_prompt, AnalysisType
from ..parsers import PatternParser

logger = logging.getLogger(__name__)

class PatternPerplexityClient(BasePerplexityClient):
    """Client for pattern detection using Perplexity API."""
    
    def __init__(self):
        super().__init__()
        self.parser = PatternParser()

    async def generate_insights(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate pattern detection insights using Perplexity."""
        try:
            # Get prompt
            prompt = get_prompt(
                analysis_type=AnalysisType.PATTERN,
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

            # Parse the response
            parsed_data = await self.parser.parse(raw_response, topic_keyword=topic_keyword, user_query=user_query)
            
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
            logger.error(f"Error generating pattern detection insights: {str(e)}", exc_info=True)
            return {
                "raw_perplexity_response": "",
                "structured_data": None
            } 