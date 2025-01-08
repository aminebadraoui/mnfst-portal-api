from typing import Dict
from pydantic import BaseModel
import logging
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic_ai.result import RunResult
from ...core.config import settings

logger = logging.getLogger(__name__)

class QueryGeneratorOutput(BaseModel):
    query: str

@dataclass
class QueryDeps:
    """Dependencies for query generation."""
    openai_api_key: str = settings.OPENAI_API_KEY

# Create a reusable agent instance
query_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=QueryDeps,
    result_type=QueryGeneratorOutput,
    system_prompt="""You are a helpful assistant that converts product descriptions into natural community discussion questions.
    Your task is to generate ONE clear, conversational question that would naturally come up in community discussions.
    The question should help uncover real user needs, problems, and behaviors in this space.
    
    The question should:
    - Use natural language people actually use online
    - Focus on problems/needs rather than specific solutions
    - Be open-ended enough to reveal unexpected insights
    - Avoid mentioning specific brands or products
    - Be something people would genuinely ask in forums/communities"""
)

class QueryGenerator:
    def __init__(self):
        logger.info("Initializing QueryGenerator")

    async def generate(
        self,
        description: str,
    ) -> QueryGeneratorOutput:
        """
        Generate a community-focused query using the provided agent.
        """
        try:
            deps = QueryDeps()
            result: RunResult[QueryGeneratorOutput] = await query_agent.run(
                f"Here's the product/service description:\n{description}",
                deps=deps
            )
            return result.data
                
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}", exc_info=True)
            raise 