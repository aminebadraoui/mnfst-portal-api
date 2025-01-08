from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseParser, ParserDeps
from pydantic_ai import Agent
from ..models.schemas.pain import PainParserResult

class PainParser(BaseParser):
    """Parser for pain & frustration analysis content."""
    
    def _init_agent(self):
        """Initialize the pain analysis parsing agent."""
        self.agent = Agent[None, PainParserResult](  # type: ignore
            model=self.model,
            result_type=PainParserResult,
            deps_type=ParserDeps,
            system_prompt="""You are a pain & frustration insights parser.
Your task is to analyze the provided content from perplexity research about pain points and frustrations.

The content will focus on:
- Most emotionally charged complaints
- Recurring sources of anger
- Hidden frustrations
- Indirect expressions of dissatisfaction
- Cascade effects of problems
- Time patterns in complaint posting

For each insight, provide:
1. A clear title/description
2. Supporting evidence (direct quotes)
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. Frequency of occurrence
6. Correlation with other patterns
7. Significance/implications

Focus on emotional impact and user frustrations.
Organize findings by engagement level (most discussed/upvoted first).""") 