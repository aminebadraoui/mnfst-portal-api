from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..models.schemas.question import QuestionParserResult
import logging

logger = logging.getLogger(__name__)

class QuestionParserDeps(BaseModel):
    """Dependencies for parsing question & advice mapping content."""
    content: str = Field(..., description="Raw perplexity research content about questions and advice")
    topic_keyword: str = Field(..., description="The main topic or product being analyzed for questions and advice")

class QuestionParser:
    """Parser for extracting question & advice insights from research content."""
    
    def __init__(self):
        """Initialize the question parser with OpenAI model."""
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()

    def _init_agent(self):
        """Initialize the question mapping parsing agent."""
        self.agent = Agent[QuestionParserDeps, QuestionParserResult](
            model=self.model,
            result_type=QuestionParserResult,
            deps_type=QuestionParserDeps,
            system_prompt="""You are a question & advice insights parser.
Your task is to analyze the provided content from perplexity research and extract structured insights about questions and advice.

For each distinct question or advice pattern you find, create an insight with:

1. Title: A clear, descriptive title summarizing the question/advice pattern
2. Question Type: Categorize as one of:
   - Product Usage (how to use specific features)
   - Troubleshooting (solving problems/errors)
   - Comparison (comparing options/alternatives)
   - Best Practices (recommended approaches)
   - Integration (working with other tools/systems)
   - Setup/Configuration
   - Performance Optimization
   - Other (specify)

3. Evidence: Direct quotes showing this question/advice pattern
4. Suggested Answers: List the most helpful/upvoted answers or solutions
5. Related Questions: Other questions commonly asked alongside this one

Focus on:
- Questions that appear multiple times in different forms
- Questions with high engagement (many responses/votes)
- Questions that lead to detailed discussions
- Questions where there's debate about the best solution
- Questions that reveal common user challenges

Structure each insight to help users:
1. Understand what others are asking about similar issues
2. Find proven solutions and workarounds
3. See related questions they should also consider
4. Identify best practices and common pitfalls

The goal is to map out the landscape of user questions and community knowledge to help others find answers more efficiently."""
        )

    async def parse(self, content: str, topic_keyword: str) -> QuestionParserResult:
        """Parse the research content and extract question & advice insights.

        Args:
            content: Raw research content about questions and advice
            topic_keyword: Main topic or product being analyzed

        Returns:
            QuestionParserResult: Structured insights about questions and advice
        """
        deps = QuestionParserDeps(content=content, topic_keyword=topic_keyword)
        result = await self.agent.arun(deps=deps)
        return result.data 