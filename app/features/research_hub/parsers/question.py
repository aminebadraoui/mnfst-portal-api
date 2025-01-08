from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseParser, ParserDeps
from pydantic_ai import Agent
from ..models.schemas.question import QuestionParserResult

class QuestionParser(BaseParser):
    """Parser for question & advice mapping content."""
    
    def _init_agent(self):
        """Initialize the question mapping parsing agent."""
        self.agent = Agent[None, QuestionParserResult](  # type: ignore
            model=self.model,
            result_type=QuestionParserResult,
            deps_type=ParserDeps,
            system_prompt="""You are a question & advice insights parser.
Your task is to analyze the provided content from perplexity research about questions and advice.

The content will focus on:
- Most frequently asked questions
- Most upvoted advice
- Most debated solutions
- Most repeated recommendations
- Success stories with details
- Failure patterns with context

For each insight, provide:
1. A clear title/description
2. Supporting evidence (direct quotes)
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. Frequency of occurrence
6. Correlation with other patterns
7. Significance/implications

Focus on what users are asking and what solutions work.
Organize findings by engagement level (most discussed/upvoted first).""") 