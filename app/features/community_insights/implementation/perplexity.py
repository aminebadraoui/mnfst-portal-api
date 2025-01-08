from typing import Dict, List, Optional, Any
import logging
import importlib
from ..prompts import templates
from ..prompts.templates import (
    get_pain_analysis_prompt,
    get_question_mapping_prompt,
    get_pattern_detection_prompt,
    get_avatars_prompt,
    get_product_analysis_prompt,
    get_failed_solutions_prompt
)
from openai import AsyncOpenAI
from ....core.config import settings

# Reload the templates module to ensure we get the latest version
importlib.reload(templates)

logger = logging.getLogger(__name__)

class PerplexityClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    async def generate_insights(
        self,
        section_type: str,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Generate insights for a specific section using Perplexity.
        Returns a structured response that can be directly stored in the database.
        """
        try:
            # Get the appropriate prompt based on section type
            prompt = self._get_section_prompt(
                section_type=section_type,
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )

            # Make API call to Perplexity (asynchronously)
            completion = await self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract content from the response
            if completion and completion.choices and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                
                # Structure the response based on section type
                if section_type == "Avatars":
                    return {
                        "raw_perplexity_response": content,
                        "structured_data": {
                            "avatars": [
                                {
                                    "name": "",  # Will be parsed later
                                    "type": "",  # Will be parsed later
                                    "insights": []  # Will be parsed later
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "raw_perplexity_response": content,
                        "structured_data": {
                            "sections": [
                                {
                                    "title": section_type,
                                    "icon": self._get_section_icon(section_type),
                                    "insights": []  # Will be parsed later
                                }
                            ]
                        }
                    }
            else:
                logger.error(f"No content received from Perplexity for {section_type}")
                return {
                    "raw_perplexity_response": "",
                    "structured_data": None
                }

        except Exception as e:
            logger.error(f"Error generating insights with Perplexity for {section_type}: {str(e)}", exc_info=True)
            return {
                "raw_perplexity_response": "",
                "structured_data": None
            }

    def _get_section_prompt(
        self,
        section_type: str,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> str:
        """Get the appropriate prompt for a section type."""
        if section_type == "Pain & Frustration Analysis":
            return get_pain_analysis_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        elif section_type == "Failed Solutions Analysis":
            return get_failed_solutions_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        elif section_type == "Question & Advice Mapping":
            return get_question_mapping_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        elif section_type == "Pattern Detection":
            return get_pattern_detection_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        elif section_type == "Popular Products Analysis":
            return get_product_analysis_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        elif section_type == "Avatars":
            return get_avatars_prompt(
                topic_keyword=topic_keyword,
                user_query=user_query,
                source_urls=source_urls,
                use_only_specified_sources=use_only_specified_sources
            )
        else:
            raise ValueError(f"Unknown section type: {section_type}") 

    def _get_section_icon(self, section_type: str) -> str:
        """
        Returns the appropriate icon for each section type.
        """
        icon_mapping = {
            "Pain & Frustration Analysis": "FaHeartBroken",
            "Failed Solutions Analysis": "FaTimesCircle",
            "Product Analysis": "FaShoppingCart",
            "Pattern Detection": "FaChartLine",
            "Question Mapping": "FaQuestionCircle",
            "Avatars": "FaUsers"
        }
        return icon_mapping.get(section_type, "FaCircle") 