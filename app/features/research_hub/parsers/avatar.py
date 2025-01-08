from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseParser, ParserDeps
from pydantic_ai import Agent
from ..models.schemas.avatar import AvatarParserResult

class AvatarParser(BaseParser):
    """Parser for avatar analysis content."""
    
    def _init_agent(self):
        """Initialize the avatar analysis parsing agent."""
        self.agent = Agent[None, AvatarParserResult](  # type: ignore
            model=self.model,
            result_type=AvatarParserResult,
            deps_type=ParserDeps,
            system_prompt="""You are an avatar insights parser.
Your task is to analyze the provided content from perplexity research about user avatars and personas.

The content will focus on:
- Distinct user types and personas
- Behavioral patterns for each avatar
- Common pain points per avatar
- Specific needs and preferences
- Decision-making patterns
- Communication styles
- Value propositions that resonate

For each avatar, provide:
1. A clear name and type
2. Supporting evidence (direct quotes)
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. Frequency of occurrence
6. Key characteristics
7. Primary motivations and goals

Focus on creating distinct, actionable user personas.
Organize findings by engagement level (most discussed/upvoted first).""") 