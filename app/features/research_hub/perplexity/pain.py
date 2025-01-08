from typing import Dict, List, Optional, Any
import logging
from .base import BasePerplexityClient
from ..prompts.templates import get_prompt, AnalysisType
from ..parsers import PainParser

logger = logging.getLogger(__name__)

class PainPerplexityClient(BasePerplexityClient):
    """Client for pain & frustration analysis using Perplexity API."""
    
    def __init__(self):
        super().__init__()
        self.parser = PainParser()

    async def generate_insights(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate pain & frustration insights using Perplexity."""
        try:
            # Get prompt
            prompt = get_prompt(
                analysis_type=AnalysisType.PAIN,
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )

            # Make API request
            content = await self._make_request(prompt)
            if not content:
                return {
                    "raw_perplexity_response": "",
                    "structured_data": None
                }

            # Parse the response
            parsed_data = await self.parser.parse(content, topic_keyword, user_query)
            
            return {
                "raw_perplexity_response": content,
                "structured_data": parsed_data
            }

        except Exception as e:
            logger.error(f"Error generating pain insights: {str(e)}", exc_info=True)
            return {
                "raw_perplexity_response": "",
                "structured_data": None
            } 