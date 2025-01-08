from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseParser, ParserDeps
from pydantic_ai import Agent
from ..models.schemas.pattern import PatternParserResult

class PatternParser(BaseParser):
    """Parser for pattern detection content."""
    
    def _init_agent(self):
        """Initialize the pattern detection parsing agent."""
        self.agent = Agent[None, PatternParserResult](  # type: ignore
            model=self.model,
            result_type=PatternParserResult,
            deps_type=ParserDeps,
            system_prompt="""You are a pattern detection insights parser.
Your task is to analyze the provided content from perplexity research about patterns and trends.

The content will focus on:
- Unusual word combinations
- Vocabulary differences between users
- Shifts in problem descriptions
- Non-obvious correlations
- Counter-intuitive success patterns
- Secondary effects users overlook
- Unexpected relationships between issues

For each insight, provide:
1. A clear title/description
2. Supporting evidence (direct quotes)
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. Frequency of occurrence
6. Correlation with other patterns
7. Significance/implications

Focus on unexpected patterns and hidden relationships.
Organize findings by engagement level (most discussed/upvoted first).""") 