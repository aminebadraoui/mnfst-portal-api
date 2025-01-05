from typing import Dict, Any
import asyncio
from openai import AsyncOpenAI, OpenAI
from ....core.celery import celery_app
from .parser import PerplexityParser
from .models import CommunityInsightsResponse
from ..prompts import get_community_insights_prompt
from ....core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="process_community_insights")
def process_community_insights(
    topic_keyword: str,
    source_urls: list = None,
    product_urls: list = None,
    use_only_specified_sources: bool = False
) -> Dict[str, Any]:
    """
    Celery task to handle both the Perplexity request and parsing.
    """
    try:
        logger.info(f"Starting community insights task for topic: {topic_keyword}")
        
        # Generate prompt
        prompt = get_community_insights_prompt(
            topic_keyword=topic_keyword,
            source_urls=source_urls,
            product_urls=product_urls,
            use_only_specified_sources=use_only_specified_sources
        )
        
        # Call Perplexity API
        perplexity_client = OpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        perplexity_response = perplexity_client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=[{"role": "user", "content": prompt}]
        )
        content = perplexity_response.choices[0].message.content
        logger.debug(f"Received response from Perplexity (first 500 chars): {content[:500]}")
        
        # Parse with GPT-4o-mini
        parser = PerplexityParser()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(parser.parse_response(content, topic_keyword))
            loop.close()
            
            # Convert Pydantic model to dict for serialization
            result = response.model_dump()
            # Add raw Perplexity response
            result["raw_perplexity_response"] = content
            logger.info(f"Successfully processed insights with {len(result['sections'])} sections")
            return result
        except Exception as e:
            logger.error(f"Error during parsing: {str(e)}")
            # Return a properly structured error response
            return {
                "status": "error",
                "sections": [],
                "avatars": [],
                "raw_perplexity_response": content,
                "error": str(e)
            }
        finally:
            if not loop.is_closed():
                loop.close()
        
    except Exception as e:
        logger.error(f"Error in process_community_insights task: {str(e)}", exc_info=True)
        # Return a properly structured error response
        return {
            "status": "error",
            "sections": [],
            "avatars": [],
            "raw_perplexity_response": content if 'content' in locals() else "",
            "error": str(e)
        } 