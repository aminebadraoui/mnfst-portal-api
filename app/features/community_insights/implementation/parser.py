from typing import Dict, Any, List
from dataclasses import dataclass
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

logger = logging.getLogger(__name__)

@dataclass
class ParserDeps:
    content: str
    topic_keyword: str

class PerplexityParser:
    def __init__(self):
        logger.info("Initializing PerplexityParser")
        try:
            self.model = OpenAIModel('gpt-4o-mini')
            logger.info("OpenAI model initialized with gpt-4o-mini")
            
            # Agent for parsing pain & frustration analysis
            self.pain_agent = Agent[None, PainAnalysisResult](  # type: ignore
                model=self.model,
                result_type=PainAnalysisResult,
                deps_type=ParserDeps,
                system_prompt="""You are a pain & frustration insights parser.
Your task is to analyze content and extract ONLY insights about user pain points and frustrations.

Focus EXCLUSIVELY on:
- Most emotionally charged complaints
- Recurring sources of anger
- Hidden frustrations
- Indirect expressions of dissatisfaction

DO NOT include insights about questions, advice, or patterns.

For each insight, include:
- A clear title describing the insight
- Direct quotes as evidence
- Source URLs in plain text
- Engagement metrics (upvotes, comments)
- How frequently this appears in discussions
- Related patterns or correlations
- The significance or impact on users""")

            # Agent for parsing question & advice mapping
            self.question_agent = Agent[None, QuestionMappingResult](  # type: ignore
                model=self.model,
                result_type=QuestionMappingResult,
                deps_type=ParserDeps,
                system_prompt="""You are a question & advice insights parser.
Your task is to analyze content and extract ONLY insights about user questions and advice.

Focus EXCLUSIVELY on:
- Most frequently asked questions
- Most upvoted advice
- Most debated solutions
- Most repeated recommendations
- Success stories with details
- Failure patterns with context

DO NOT include insights about pain points, frustrations, or general patterns.

For each insight, include:
- A clear title describing the insight
- Direct quotes as evidence
- Source URLs in plain text
- Engagement metrics (upvotes, comments)
- How frequently this appears in discussions
- Related patterns or correlations
- The significance or impact on users""")

            # Agent for parsing pattern detection
            self.pattern_agent = Agent[None, PatternDetectionResult](  # type: ignore
                model=self.model,
                result_type=PatternDetectionResult,
                deps_type=ParserDeps,
                system_prompt="""You are a pattern detection insights parser.
Your task is to analyze content and extract ONLY insights about patterns and trends.

Focus EXCLUSIVELY on:
- Unusual word combinations
- Vocabulary differences between users
- Shifts in problem descriptions
- Non-obvious correlations
- Counter-intuitive success patterns
- Secondary effects users overlook
- Unexpected relationships between issues

DO NOT include insights about pain points, questions, or advice.

For each insight, include:
- A clear title describing the insight
- Direct quotes as evidence
- Source URLs in plain text
- Engagement metrics (upvotes, comments)
- How frequently this appears in discussions
- Related patterns or correlations
- The significance or impact on users""")

            # Agent for parsing avatars
            self.avatars_agent = Agent[None, AvatarsResult](  # type: ignore
                model=self.model,
                result_type=AvatarsResult,
                deps_type=ParserDeps,
                system_prompt="""You are an avatar parser focused on identifying distinct user types from discussions.
Your task is to analyze content and identify unique user personas based on:

- How they describe their experiences
- What solutions they seek
- Their approach to problems
- Their interaction patterns
- Their decision-making process

For each identified avatar:
- Give them a descriptive name that captures their essence
- Create a profile based on actual quotes
- Document their specific needs and challenges
- Note their typical behaviors
- Include supporting evidence with sources
- List their pain points
- Describe their decision-making process

Focus on creating distinct, non-overlapping avatars that capture major user segments evident in the discussions.""")

            # Agent for parsing product analysis
            self.product_agent = Agent[None, ProductAnalysisResult](  # type: ignore
                model=self.model,
                result_type=ProductAnalysisResult,
                deps_type=ParserDeps,
                system_prompt="""You are a product analysis parser focused on popular products and market opportunities.
Your task is to analyze content and extract insights about products from Amazon, eBay, and Google Shopping.

Focus EXCLUSIVELY on:
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
- Market significance

Focus on identifying patterns in customer feedback and market opportunities.""")

            # Agent for parsing failed solutions
            self.failed_solutions_agent = Agent[None, FailedSolutionsResult](  # type: ignore
                model=self.model,
                result_type=FailedSolutionsResult,
                deps_type=ParserDeps,
                system_prompt="""You are a failed solutions parser focused on identifying unsuccessful attempts and approaches.
Your task is to analyze content and extract insights about solutions that didn't work.

Focus EXCLUSIVELY on:
- Most common failed approaches
- Solutions that made problems worse
- Abandoned treatment methods
- Wasted investments
- Ineffective products or services
- Misguided advice that backfired
- Common mistakes and pitfalls

For each failed solution insight, include:
- A clear title describing what failed
- Direct quotes as evidence
- Source URL in plain text
- Engagement metrics (upvotes, comments)
- How frequently this failure appears
- Related patterns or correlations
- The significance or impact on users

Focus on understanding why these solutions failed and what can be learned.""")

            logger.info("Pydantic AI agents initialized with system prompts")
        except Exception as e:
            logger.error(f"Error initializing PerplexityParser: {str(e)}", exc_info=True)
            raise

    async def parse_pain_analysis(self, content: str, topic_keyword: str) -> PainAnalysisResult:
        """
        Parse pain & frustration analysis insights.
        """
        try:
            logger.info("Starting to parse pain & frustration analysis")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.pain_agent.run(
                f"""Extract pain & frustration insights from this content:

{content}

Topic: {topic_keyword}

Return insights in this format:
{{
  "title": "Pain & Frustration Analysis",
  "icon": "FaExclamationCircle",
  "insights": [
    {{
      "title": "Clear title of the insight",
      "evidence": "Direct quote from the content",
      "source_url": "Source URL in plain text",
      "engagement_metrics": "Upvotes, comments, etc.",
      "frequency": "How often this appears",
      "correlation": "Related patterns",
      "significance": "Impact on users"
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from pain agent")
                return PainAnalysisResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_pain_analysis: {str(e)}", exc_info=True)
            return PainAnalysisResult()

    async def parse_question_mapping(self, content: str, topic_keyword: str) -> QuestionMappingResult:
        """
        Parse question & advice mapping insights.
        """
        try:
            logger.info("Starting to parse question & advice mapping")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.question_agent.run(
                f"""Extract question & advice insights from this content:

{content}

Topic: {topic_keyword}

Return insights in this format:
{{
  "title": "Question & Advice Mapping",
  "icon": "FaQuestionCircle",
  "insights": [
    {{
      "title": "Clear title of the insight",
      "evidence": "Direct quote from the content",
      "source_url": "Source URL in plain text",
      "engagement_metrics": "Upvotes, comments, etc.",
      "frequency": "How often this appears",
      "correlation": "Related patterns",
      "significance": "Impact on users"
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from question agent")
                return QuestionMappingResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_question_mapping: {str(e)}", exc_info=True)
            return QuestionMappingResult()

    async def parse_pattern_detection(self, content: str, topic_keyword: str) -> PatternDetectionResult:
        """
        Parse pattern detection insights.
        """
        try:
            logger.info("Starting to parse pattern detection")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.pattern_agent.run(
                f"""Extract pattern detection insights from this content:

{content}

Topic: {topic_keyword}

Return insights in this format:
{{
  "title": "Pattern Detection",
  "icon": "FaChartLine",
  "insights": [
    {{
      "title": "Clear title of the insight",
      "evidence": "Direct quote from the content",
      "source_url": "Source URL in plain text",
      "engagement_metrics": "Upvotes, comments, etc.",
      "frequency": "How often this appears",
      "correlation": "Related patterns",
      "significance": "Impact on users"
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from pattern agent")
                return PatternDetectionResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_pattern_detection: {str(e)}", exc_info=True)
            return PatternDetectionResult()

    async def parse_avatars(self, content: str, topic_keyword: str) -> AvatarsResult:
        """
        Parse avatars from Perplexity response.
        """
        try:
            logger.info("Starting to parse avatars")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.avatars_agent.run(
                f"""Extract avatars from this content:

{content}

Topic: {topic_keyword}

Return avatars in this format:
{{
  "avatars": [
    {{
      "name": "Descriptive name of the avatar",
      "type": "Category/type of user",
      "insights": [
        {{
          "title": "Key Characteristics",
          "description": "Detailed profile of this user type",
          "evidence": "Direct quotes that support this profile",
          "needs": ["List of specific needs"],
          "pain_points": ["List of pain points"],
          "behaviors": ["List of typical behaviors"]
        }}
      ]
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from avatars agent")
                return AvatarsResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_avatars: {str(e)}", exc_info=True)
            return AvatarsResult()

    async def parse_product_analysis(self, content: str, topic_keyword: str) -> ProductAnalysisResult:
        """
        Parse product analysis insights.
        """
        try:
            logger.info("Starting to parse product analysis")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.product_agent.run(
                f"""Extract product analysis insights from this content:

{content}

Topic: {topic_keyword}

Return insights in this format:
{{
  "title": "Popular Products Analysis",
  "icon": "FaShoppingCart",
  "insights": [
    {{
      "title": "Product name and description",
      "platform": "Amazon/eBay/Google Shopping",
      "price_range": "Price range",
      "positive_feedback": ["List of positive points"],
      "negative_feedback": ["List of negative points"],
      "market_gap": "Identified market opportunity",
      "source_url": "Source URL in plain text",
      "engagement_metrics": "Reviews, ratings, etc.",
      "frequency": "How often mentioned",
      "correlation": "Related products/patterns",
      "significance": "Market impact"
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from product agent")
                return ProductAnalysisResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_product_analysis: {str(e)}", exc_info=True)
            return ProductAnalysisResult()

    async def parse_failed_solutions(self, content: str, topic_keyword: str) -> FailedSolutionsResult:
        """
        Parse failed solutions insights.
        """
        try:
            logger.info("Starting to parse failed solutions")
            deps = ParserDeps(content=content, topic_keyword=topic_keyword)

            result = await self.failed_solutions_agent.run(
                f"""Extract failed solutions insights from this content:

{content}

Topic: {topic_keyword}

Return insights in this format:
{{
  "title": "Failed Solutions Analysis",
  "icon": "FaTimesCircle",
  "insights": [
    {{
      "title": "Clear title of the failed solution",
      "evidence": "Direct quote from the content",
      "source_url": "Source URL in plain text",
      "engagement_metrics": "Upvotes, comments, etc.",
      "frequency": "How often this appears",
      "correlation": "Related patterns",
      "significance": "Impact on users"
    }}
  ]
}}""",
                deps=deps
            )
            
            if result is None or result.data is None:
                logger.warning("Received None response from failed solutions agent")
                return FailedSolutionsResult()
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error in parse_failed_solutions: {str(e)}", exc_info=True)
            return FailedSolutionsResult()

    # For backward compatibility
    async def parse_insights(self, pain_content: str, question_content: str, pattern_content: str, topic_keyword: str) -> ParserResult:
        """
        Parse all insights sections from separate outputs.
        """
        # Parse each section separately
        pain_result = await self.parse_pain_analysis(pain_content, topic_keyword)
        question_result = await self.parse_question_mapping(question_content, topic_keyword)
        pattern_result = await self.parse_pattern_detection(pattern_content, topic_keyword)
        
        # Convert to InsightSection format
        sections = [
            InsightSection(
                title=pain_result.title,
                icon=pain_result.icon,
                insights=[insight.dict() for insight in pain_result.insights]
            ),
            InsightSection(
                title=question_result.title,
                icon=question_result.icon,
                insights=[insight.dict() for insight in question_result.insights]
            ),
            InsightSection(
                title=pattern_result.title,
                icon=pattern_result.icon,
                insights=[insight.dict() for insight in pattern_result.insights]
            )
        ]
        
        return ParserResult(
            status="completed",
            sections=sections,
            raw_perplexity_response=f"""Pain Analysis:
{pain_content}

Question Mapping:
{question_content}

Pattern Detection:
{pattern_content}"""
        )

    # For backward compatibility
    async def parse_response(self, pain_content: str, question_content: str, pattern_content: str, avatars_content: str, topic_keyword: str) -> ParserResult:
        """
        Parse insights and avatars from separate outputs.
        """
        # Parse insights and avatars separately
        insights_result = await self.parse_insights(pain_content, question_content, pattern_content, topic_keyword)
        avatars_result = await self.parse_avatars(avatars_content, topic_keyword)
        
        # Convert AvatarsResult to list of Avatar
        avatars = [
            Avatar(
                name=avatar.name,
                type=avatar.type,
                insights=[
                    AvatarInsight(
                        title=insight.title,
                        description=insight.description,
                        evidence=insight.evidence,
                        needs=insight.needs,
                        pain_points=insight.pain_points,
                        behaviors=insight.behaviors
                    ) for insight in avatar.insights
                ]
            ) for avatar in avatars_result.avatars
        ]
        
        insights_result.avatars = avatars
        return insights_result 