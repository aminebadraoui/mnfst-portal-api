from typing import Dict
from pydantic import BaseModel
import logging
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ....core.config import settings

logger = logging.getLogger(__name__)

class QueryGeneratorInput(BaseModel):
    description: str

class QueryGenerator:
    def __init__(self):
        logger.info("Initializing QueryGenerator")
        try:
            self.model = OpenAIModel('gpt-4o-mini')
            logger.info("OpenAI model initialized with gpt-4o-mini")
            
            self.agent = Agent(
                model=self.model,
                system_prompt="""You are a helpful assistant that converts product descriptions into natural community discussion questions.
                Your task is to generate ONE clear, conversational question that would naturally come up in community discussions.
                The question should help uncover real user needs, problems, and behaviors in this space."""
            )
            logger.info("Pydantic AI agent initialized with system prompt")
        except Exception as e:
            logger.error(f"Error initializing QueryGenerator: {str(e)}", exc_info=True)
            raise

    async def generate(self, description: str) -> Dict[str, str]:
        """
        Use GPT-4-0125-mini to generate a community-focused query.
        """
        try:
            logger.info("Starting to generate query")
            logger.debug(f"Description length: {len(description)} characters")
            
            # Create generator input
            generator_input = QueryGeneratorInput(description=description)
            logger.debug(f"Created generator input: {generator_input.model_dump_json()}")
            
            # Run generator
            logger.info("Running GPT-4-0125-mini generator")
            try:
                prompt = f"""Convert this product/service description into ONE clear, conversational question that would naturally come up in community discussions.

The question should:
- Use natural language people actually use online
- Focus on problems/needs rather than specific solutions
- Be open-ended enough to reveal unexpected insights
- Avoid mentioning specific brands or products
- Be something people would genuinely ask in forums/communities

Here's the product/service description:
{description}"""

                result = await self.agent.run(prompt)
                logger.debug(f"Raw generator response: {result}")
                
                if result is None:
                    logger.warning("Received None response from agent")
                    return {"query": ""}
                
                # Extract query from RunResult
                if hasattr(result, '_all_messages'):
                    for message in result._all_messages:
                        if hasattr(message, 'parts'):
                            for part in message.parts:
                                if hasattr(part, 'content') and part.part_kind == 'text':
                                    generated_query = part.content.strip()
                                    logger.info(f"Generated query: {generated_query}")
                                    return {"query": generated_query}
                
                # Fallback to string representation if structure is different
                generated_query = str(result).strip()
                logger.info(f"Generated query (fallback): {generated_query}")
                return {"query": generated_query}
                
            except Exception as e:
                logger.error(f"Error during GPT-4-0125-mini generation: {str(e)}", exc_info=True)
                raise
                
        except Exception as e:
            logger.error(f"Error in generate: {str(e)}", exc_info=True)
            raise 