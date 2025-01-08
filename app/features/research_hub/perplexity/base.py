from typing import Dict, List, Optional, Any
import logging
from openai import AsyncOpenAI
from ....core.config import settings

logger = logging.getLogger(__name__)

class BasePerplexityClient:
    """Base class for all Perplexity API clients."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    async def _make_request(self, prompt: str) -> Optional[str]:
        """Make a request to the Perplexity API."""
        try:
            completion = await self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=[{"role": "user", "content": prompt}]
            )

            if completion and completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                logger.error("No content received from Perplexity")
                return None

        except Exception as e:
            logger.error(f"Error making request to Perplexity API: {str(e)}", exc_info=True)
            return None

    async def generate_insights(
        self,
        topic_keyword: str,
        user_query: str,
        source_urls: Optional[List[str]] = None,
        product_urls: Optional[List[str]] = None,
        use_only_specified_sources: bool = False
    ) -> Dict[str, Any]:
        """Generate insights using the Perplexity API. Should be implemented by child classes."""
        raise NotImplementedError("Child classes must implement generate_insights") 