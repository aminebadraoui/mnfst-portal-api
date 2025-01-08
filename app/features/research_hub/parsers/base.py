from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from ....core.config import settings

logger = logging.getLogger(__name__)

class ParserDeps(BaseModel):
    """Dependencies for parsing perplexity research content."""
    content: str = Field(..., description="Raw perplexity research content")
    topic_keyword: str = Field(..., description="The main topic being analyzed")

class BaseParser:
    """Base class for all content parsers."""
    def __init__(self):
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()

    def _init_agent(self):
        """Initialize the parsing agent. Should be implemented by child classes."""
        raise NotImplementedError("Child classes must implement _init_agent")

    async def parse(self, content: str, topic_keyword: str, user_query: str) -> Dict[str, Any]:
        """Parse the content into structured insights."""
        try:
            deps = ParserDeps(
                content=content,
                topic_keyword=topic_keyword
            )
            
            result = await self.agent.run(content, deps=deps)
            
            if result and result.data:
                parsed_data = result.data.dict()
                # Add query to each insight
                if parsed_data.get("insights"):
                    for insight in parsed_data["insights"]:
                        insight["query"] = user_query
                
                return parsed_data
            else:
                logger.warning(f"No data returned from agent for {self.__class__.__name__}")
                return {"insights": []}

        except Exception as e:
            logger.error(f"Error parsing content with {self.__class__.__name__}: {str(e)}", exc_info=True)
            return {"insights": []} 