from typing import List, Optional
from pydantic import HttpUrl
import logging

logger = logging.getLogger(__name__)

def get_community_insights_prompt(
    topic_keyword: str,
    source_urls: Optional[List[HttpUrl]] = None,
    product_urls: Optional[List[HttpUrl]] = None,
    use_only_specified_sources: bool = False
) -> str:
    """
    Generate a prompt for the AI model to analyze community insights.
    """
    logger.info(f"Generating prompt for topic: {topic_keyword}")
    
    base_prompt = f"""Analyze community discussions and provide comprehensive insights about {topic_keyword}.
Focus on identifying:
1. Pain points and frustrations
2. Common questions and advice patterns
3. Emerging trends and patterns
4. Competitive landscape and market positioning

For each insight, provide:
- Supporting evidence from discussions
- Source of information
- Engagement metrics
- Frequency of mention
- Correlation with other topics
- Business significance
"""

    if source_urls:
        urls_str = "\n".join([f"- {url}" for url in source_urls])
        base_prompt += f"\n\nAnalyze the following specific sources:\n{urls_str}"
        logger.info(f"Added {len(source_urls)} source URLs to prompt")
    
    if product_urls:
        urls_str = "\n".join([f"- {url}" for url in product_urls])
        base_prompt += f"\n\nInclude analysis of these product pages:\n{urls_str}"
        logger.info(f"Added {len(product_urls)} product URLs to prompt")
    
    if use_only_specified_sources:
        base_prompt += "\n\nOnly use the specified URLs for analysis. Do not include information from other sources."
        logger.info("Set to use only specified sources")
    else:
        base_prompt += "\n\nIn addition to any specified sources, include relevant insights from other reliable sources."
        logger.info("Set to include additional sources")

    logger.debug(f"Final prompt: {base_prompt}")
    return base_prompt 