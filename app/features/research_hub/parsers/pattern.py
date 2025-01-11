from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..models.schemas.pattern import PatternParserResult
import logging

logger = logging.getLogger(__name__)

class PatternParserDeps(BaseModel):
    """Dependencies for parsing pattern detection content."""
    content: str = Field(..., description="Raw perplexity research content about patterns and trends")
    topic_keyword: str = Field(..., description="The main topic or product being analyzed for patterns")

class PatternParser:
    """Parser for extracting pattern & trend insights from research content."""
    
    def __init__(self):
        """Initialize the pattern parser with OpenAI model."""
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()

    def _init_agent(self):
        """Initialize the pattern detection parsing agent."""
        self.agent = Agent[PatternParserDeps, PatternParserResult](
            model=self.model,
            result_type=PatternParserResult,
            deps_type=PatternParserDeps,
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
Organize findings by engagement level (most discussed/upvoted first)."""
        )

    async def parse(self, content: str, topic_keyword: str) -> PatternParserResult:
        """Parse the research content and extract pattern & trend insights.

        Args:
            content: Raw research content about patterns and trends
            topic_keyword: Main topic or product being analyzed

        Returns:
            PatternParserResult: Structured insights about patterns and trends
        """
        deps = PatternParserDeps(content=content, topic_keyword=topic_keyword)
        result = await self.agent.arun(deps=deps)
        return result.data 