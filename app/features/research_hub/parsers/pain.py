from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ..models.schemas.pain import PainParserResult, PainInsight
import logging

logger = logging.getLogger(__name__)

class PainParserDeps(BaseModel):
    """Dependencies for parsing pain & frustration analysis content."""
    content: str = Field(..., description="Raw perplexity research content about pain points and frustrations")
    topic_keyword: str = Field(..., description="The main topic or product being analyzed for pain points")

class PainParser:
    """Parser for extracting pain & frustration insights from research content."""
    
    def __init__(self):
        """Initialize the pain parser with OpenAI model."""
        self.model = OpenAIModel('gpt-4o-mini')
        self._init_agent()

    def _init_agent(self):
        """Initialize the pain analysis parsing agent."""
        self.agent = Agent[PainParserDeps, PainParserResult](
            model=self.model,
            result_type=PainParserResult,
            deps_type=PainParserDeps,
            system_prompt="""You are a pain & frustration insights parser.
Your task is to analyze the provided content from perplexity research about pain points and frustrations.

The content will focus on:
- Most emotionally charged complaints
- Recurring sources of anger
- Hidden frustrations
- Cascade effects of problems

For each pain point identified, you must provide:
1. Title and severity (critical/major/minor)
2. Direct quote showing the pain point
3. Impact on user experience (with supporting quote)
4. Common workarounds (with example quote) if available
5. Source URL and engagement metrics

Requirements:
- Every insight MUST have a direct quote as evidence
- Severity must be one of: critical, major, minor
- Impact must explain the consequences of the pain point
- Impact must have its own supporting quote (different from the pain point quote)
- Engagement metrics should include upvotes and comments when available
- Organize findings by severity level

Example format:
{
    "title": "Medication Resistance Development",
    "severity": "critical",
    "pain_quote": "I've tried every medication under the sun, and nothing seems to work for more than a few days",
    "impact": "Patients lose hope in treatment efficacy and may stop seeking medical help",
    "impact_quote": "After so many failed treatments, I've almost given up on finding something that works",
    "workaround": "Rotating between different medications to prevent resistance",
    "workaround_quote": "I switch between three different medications every few weeks, which seems to help a bit",
    "source_url": "https://example.com/thread/123",
    "engagement": {"upvotes": 245, "comments": 89}
}"""
        )

    async def parse(self, content: str, topic_keyword: str) -> PainParserResult:
        """Parse the research content and extract pain & frustration insights.

        Args:
            content: Raw research content about pain points and frustrations
            topic_keyword: Main topic or product being analyzed

        Returns:
            PainParserResult: Structured insights about pain points and frustrations
        """
        deps = PainParserDeps(content=content, topic_keyword=topic_keyword)
        result = await self.agent.arun(deps=deps)
        return result.data 