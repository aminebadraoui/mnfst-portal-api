from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from ....core.config import settings
from .base_models import (
    InsightSection, Avatar, AvatarInsight, InsightItem,
    PainAnalysisResult, QuestionMappingResult, PatternDetectionResult, AvatarsResult,
    PainInsight, QuestionInsight, PatternInsight, AvatarResult, AvatarProfile,
    ParserResult, ParserInput, ProductAnalysisResult, FailedSolutionsResult
)
import json

logger = logging.getLogger(__name__)

class ParserDeps(BaseModel):
    """Dependencies for parsing perplexity research content."""
    content: str = Field(..., description="Raw perplexity research content")
    topic_keyword: str = Field(..., description="The main topic being analyzed")

class PerplexityParser:
    def __init__(self):
        logger.info("Initializing PerplexityParser")
        try:
            self.model = OpenAIModel('gpt-4o-mini')
            logger.info("OpenAI model initialized with gpt-4o-mini")
            
            # Initialize agents for each section type
            self._init_agents()
            logger.info("Pydantic AI agents initialized with system prompts")
        except Exception as e:
            logger.error(f"Error initializing PerplexityParser: {str(e)}", exc_info=True)
            raise

    async def process_section(
        self,
        section_type: str,
        content: str,
        topic_keyword: str,
        user_query: str,
    ) -> Dict[str, Any]:
        """Process content into structured insights for a section."""
        logger.info(f"Processing section: {section_type} with query: {user_query}")
        
        try:
            # Create parser dependencies
            deps = ParserDeps(
                content=content,
                topic_keyword=topic_keyword
            )
            
            # Process with appropriate agent based on section type
            logger.info(f"Processing with agent for {section_type}")
            result = None
            
            if section_type == "Pain & Frustration Analysis":
                result = await self.pain_agent.run(content, deps=deps)
                logger.info(f"Pain agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
            elif section_type == "Failed Solutions Analysis":
                result = await self.failed_solutions_agent.run(content, deps=deps)
                logger.info(f"Failed solutions agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
            elif section_type == "Question & Advice Mapping":
                result = await self.question_agent.run(content, deps=deps)
                logger.info(f"Question agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
            elif section_type == "Pattern Detection":
                result = await self.pattern_agent.run(content, deps=deps)
                logger.info(f"Pattern agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
            elif section_type == "Popular Products Analysis":
                result = await self.product_agent.run(content, deps=deps)
                logger.info(f"Product agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
            elif section_type == "Avatars":
                result = await self.avatars_agent.run(content, deps=deps)
                logger.info(f"Avatars agent result: {json.dumps(result.data.dict() if result and result.data else {})}")
                # For avatars, return them in the avatars field
                avatars_data = result.data.dict().get("avatars", []) if result and result.data else []
                # Add query to each avatar's insights
                for avatar in avatars_data:
                    if avatar.get("insights"):
                        for insight in avatar["insights"]:
                            insight["query"] = user_query
                            logger.info(f"Added query {user_query} to avatar insight: {insight.get('title', 'No title')}")
                return {
                    "section": None,
                    "avatars": avatars_data,
                    "raw_response": content
                }
            else:
                raise ValueError(f"Unknown section type: {section_type}")
            
            # Format and return results for non-avatar sections
            if result and result.data:
                section_data = result.data.dict()
                # Ensure the section has the correct title and icon
                section_data["title"] = section_type
                section_data["icon"] = self._get_section_icon(section_type)
                
                # Add query to each insight
                if section_data.get("insights"):
                    for insight in section_data["insights"]:
                        insight["query"] = user_query
                        logger.info(f"Added query {user_query} to insight: {insight.get('title', 'No title')}")
                
                # Log the final section data
                logger.info(f"Final section data for {section_type}: {json.dumps(section_data)}")
                
                return {
                    "section": section_data,
                    "avatars": [],
                    "raw_response": content
                }
            else:
                logger.warning(f"No data returned from agent for {section_type}")
                return {
                    "section": {
                        "title": section_type,
                        "icon": self._get_section_icon(section_type),
                        "insights": []
                    },
                    "avatars": [],
                    "raw_response": content
                }

        except Exception as e:
            logger.error(f"Error processing section {section_type}: {str(e)}", exc_info=True)
            return {
                "section": {
                    "title": section_type,
                    "icon": self._get_section_icon(section_type),
                    "insights": []
                },
                "avatars": [],
                "raw_response": ""
            }

    def _get_section_icon(self, section_type: str) -> str:
        """Get the icon for a section type."""
        icons = {
            "Pain & Frustration Analysis": "FaExclamationCircle",
            "Failed Solutions Analysis": "FaTimesCircle",
            "Question & Advice Mapping": "FaQuestionCircle",
            "Pattern Detection": "FaChartLine",
            "Popular Products Analysis": "FaShoppingCart"
        }
        return icons.get(section_type, "FaCircle") 

    def _init_agents(self):
        """Initialize all parsing agents."""
        # Agent for parsing pain & frustration analysis
        self.pain_agent = Agent[None, PainAnalysisResult](  # type: ignore
            model=self.model,
            result_type=PainAnalysisResult,
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

        # Agent for parsing question & advice mapping
        self.question_agent = Agent[None, QuestionMappingResult](  # type: ignore
            model=self.model,
            result_type=QuestionMappingResult,
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

        # Agent for parsing pattern detection
        self.pattern_agent = Agent[None, PatternDetectionResult](  # type: ignore
            model=self.model,
            result_type=PatternDetectionResult,
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

        # Agent for parsing product analysis
        self.product_agent = Agent[None, ProductAnalysisResult](  # type: ignore
            model=self.model,
            result_type=ProductAnalysisResult,
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

For each product insight, include:
- Product name and description
- Platform (Amazon/eBay/Google Shopping)
- Price range
- List of positive feedback points
- List of negative feedback points
- Identified market gap or opportunity
- Source URL in plain text
- Engagement metrics (reviews, ratings)
- Frequency of mentions
- Correlation with other products
- Market significance""")

        # Agent for parsing failed solutions
        self.failed_solutions_agent = Agent[None, FailedSolutionsResult](  # type: ignore
            model=self.model,
            result_type=FailedSolutionsResult,
            deps_type=ParserDeps,
            system_prompt="""You are a failed solutions parser.
Your task is to analyze the provided content from perplexity research about failed solutions and attempts.

The content will focus on:
- Most common failed approaches
- Solutions that made problems worse
- Abandoned treatment methods
- Wasted investments
- Ineffective products or services
- Misguided advice that backfired
- Common mistakes and pitfalls

For each insight, provide:
1. A clear title describing the failed solution
2. Direct quotes as evidence
3. Source URL in plain text
4. Engagement metrics (upvotes, comments)
5. How frequently this failure appears
6. Related patterns or correlations
7. The significance or impact on users

Focus on understanding why these solutions failed and what can be learned.
Organize findings by frequency and impact level.""")

        # Agent for parsing avatars
        self.avatars_agent = Agent[None, AvatarsResult](  # type: ignore
            model=self.model,
            result_type=AvatarsResult,
            deps_type=ParserDeps,
            system_prompt="""You are an avatars insights parser.
Your task is to analyze the provided content from perplexity research to identify distinct user personas or avatars.

The content will focus on:
- Distinct user types and personas
- Common behavioral patterns
- Shared pain points and needs
- Typical user journeys
- Decision-making patterns
- Success and failure stories
- Interaction styles

For each avatar, provide:
1. A descriptive name/title
2. Type/category of user
3. Key insights about their behavior
4. Supporting evidence (direct quotes)
5. Primary needs and motivations
6. Common pain points
7. Typical behaviors and patterns
8. Source URLs for evidence

Focus on creating distinct, well-defined personas that represent different user segments.
Ensure each avatar is backed by evidence from the research.""") 