from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..models.schemas.product import ProductParserResult
import logging

logger = logging.getLogger(__name__)

class ProductParserDeps(BaseModel):
    """Dependencies for parsing product analysis content."""
    content: str = Field(..., description="Raw perplexity research content about products and market opportunities")
    topic_keyword: str = Field(..., description="The main topic or product being analyzed for market insights")

class ProductParser:
    """Parser for product analysis content."""
    
    def __init__(self):
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()
    
    async def parse(self, content: Dict[str, Any], topic_keyword: Optional[str] = None, user_query: Optional[str] = None) -> ProductParserResult:
        """Parse the content into structured product insights using the agent."""
        try:
            # Create parser dependencies
            deps = ProductParserDeps(
                content=content,
                topic_keyword=topic_keyword or ""
            )
            
            # Use the agent to parse the content
            result = await self.agent.run(content, deps=deps)
            
            if result and result.data:
                parsed_data = result.data.dict()
                
                # Process each product insight
                if parsed_data.get("insights"):
                    for insight in parsed_data["insights"]:
                        # Add query to the insight
                        insight["query"] = user_query
                        
                        # Ensure all required fields are present with defaults
                        insight.update({
                            "summary": insight.get("summary", ""),
                            "value_quote": insight.get("value_quote", ""),
                            "strengths": insight.get("strengths", ""),
                            "praise_quote": insight.get("praise_quote", ""),
                            "success_case": insight.get("success_case"),
                            "success_quote": insight.get("success_quote"),
                            "limitations": insight.get("limitations", ""),
                            "criticism_quote": insight.get("criticism_quote", ""),
                            "source_url": insight.get("source_url", ""),
                            "engagement": insight.get("engagement", {"reviews": 0, "ratings": 0})
                        })
                
                return ProductParserResult(**parsed_data)
            else:
                logger.warning("No data returned from agent")
                return ProductParserResult(insights=[])
            
        except Exception as e:
            logger.error(f"Error parsing content: {str(e)}", exc_info=True)
            return ProductParserResult(insights=[])
    
    def _init_agent(self):
        """Initialize the product analysis parsing agent."""
        self.agent = Agent[None, ProductParserResult](  # type: ignore
            model=self.model,
            result_type=ProductParserResult,
            deps_type=ProductParserDeps,
            system_prompt="""You are a product insights parser.
Your task is to analyze the provided content from perplexity research about products and market analysis.

For each product, extract and structure the following information:

1. Core Information:
- Clear summary of the product
- Quote showing product value
- Key strengths and benefits
- Quote praising the product

2. Success Stories:
- Example of successful use (if available)
- Quote showing success

3. Limitations:
- Main limitations or drawbacks
- Quote showing limitations

4. Validation:
- Review metrics
- Rating distribution
- Source attribution

Organize findings by:
1. Most popular products
2. Highest rated solutions
3. Strategic importance

Ensure each insight is supported by:
- Direct quotes from users
- Clear examples
- Engagement metrics
- Source attribution""") 