from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseParser, ParserDeps
from pydantic_ai import Agent
from ..models.schemas.product import ProductParserResult

class ProductParser(BaseParser):
    """Parser for product analysis content."""
    
    def _init_agent(self):
        """Initialize the product analysis parsing agent."""
        self.agent = Agent[None, ProductParserResult](  # type: ignore
            model=self.model,
            result_type=ProductParserResult,
            deps_type=ParserDeps,
            system_prompt="""You are a product analysis parser.
Your task is to analyze the provided content from perplexity research about products and market opportunities.

The content will focus on:
- Most popular products in the category
- Price ranges and variations
- Common positive feedback themes
- Recurring complaints and issues
- Potential market gaps and opportunities
- Customer satisfaction patterns
- Feature comparisons between products

For each insight, provide:
1. A clear title/description
2. Supporting evidence (direct quotes)
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. Frequency of occurrence
6. Correlation with other patterns
7. Significance/implications

Focus on product insights and market opportunities.
Organize findings by engagement level (most discussed/upvoted first).""") 