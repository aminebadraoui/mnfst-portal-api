from typing import Dict, List, Optional, Any
import logging
from .parser import PerplexityParser
from ..prompts.templates import (
    get_pain_analysis_prompt,
    get_question_mapping_prompt,
    get_pattern_detection_prompt,
    get_avatars_prompt,
    get_product_analysis_prompt,
    get_failed_solutions_prompt
)
from openai import OpenAI
from ....core.config import settings

logger = logging.getLogger(__name__)

class PerplexityClient:
    def __init__(self):
        self.parser = PerplexityParser()
        self.client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    def generate_insights(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Generate insights using Perplexity.
        """
        try:
            # Get pain analysis
            pain_prompt = get_pain_analysis_prompt(topic_keyword=topic_keyword)
            pain_response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": pain_prompt}]
            )
            pain_content = pain_response.choices[0].message.content

            # Get question mapping
            question_prompt = get_question_mapping_prompt(topic_keyword=topic_keyword)
            question_response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": question_prompt}]
            )
            question_content = question_response.choices[0].message.content

            # Get pattern detection
            pattern_prompt = get_pattern_detection_prompt(topic_keyword=topic_keyword)
            pattern_response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": pattern_prompt}]
            )
            pattern_content = pattern_response.choices[0].message.content

            # Get avatars
            avatars_prompt = get_avatars_prompt(topic_keyword=topic_keyword)
            avatars_response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": avatars_prompt}]
            )
            avatars_content = avatars_response.choices[0].message.content

            # Parse all insights
            result = self.parser.parse_response(
                pain_content=pain_content,
                question_content=question_content,
                pattern_content=pattern_content,
                avatars_content=avatars_content,
                topic_keyword=topic_keyword
            )

            return {
                "sections": result.sections,
                "avatars": result.avatars,
                "raw_perplexity_response": result.raw_perplexity_response
            }
        except Exception as e:
            logger.error(f"Error generating insights with Perplexity: {str(e)}", exc_info=True)
            raise 