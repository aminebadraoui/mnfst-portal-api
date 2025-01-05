from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging
import json
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from ....core.config import settings
from .base_models import InsightSection, Avatar, AvatarInsight, InsightItem

logger = logging.getLogger(__name__)

class ParserInput(BaseModel):
    content: str
    topic_keyword: str

class ParserResult(BaseModel):
    status: str = "completed"
    sections: List[InsightSection] = Field(default=[
        InsightSection(
            title="Pain & Frustration Analysis",
            icon="FaExclamationCircle",
            insights=[{
                "title": "Analysis pending...",
                "evidence": "No evidence collected yet",
                "source_url": None,
                "engagement_metrics": None,
                "frequency": None,
                "correlation": None,
                "significance": None
            }]
        ),
        InsightSection(
            title="Question & Advice Mapping",
            icon="FaQuestionCircle",
            insights=[{
                "title": "Analysis pending...",
                "evidence": "No evidence collected yet",
                "source_url": None,
                "engagement_metrics": None,
                "frequency": None,
                "correlation": None,
                "significance": None
            }]
        ),
        InsightSection(
            title="Pattern Detection",
            icon="FaChartLine",
            insights=[{
                "title": "Analysis pending...",
                "evidence": "No evidence collected yet",
                "source_url": None,
                "engagement_metrics": None,
                "frequency": None,
                "correlation": None,
                "significance": None
            }]
        )
    ])
    avatars: List[Avatar] = Field(default=[
        Avatar(
            name="Desperate Seeker",
            type="Avatar",
            insights=[
                AvatarInsight(
                    title="Seeking Pain Relief",
                    description="Analysis pending...",
                    evidence="No evidence collected yet",
                    needs=["Effective pain relief", "Mobility improvement", "Quality of life"],
                    pain_points=["Chronic pain", "Failed treatments", "Loss of independence"],
                    behaviors=["Seeking multiple solutions", "Frequent forum participation"]
                )
            ]
        ),
        Avatar(
            name="Informed Seeker",
            type="Avatar",
            insights=[
                AvatarInsight(
                    title="Research-Based Solutions",
                    description="Analysis pending...",
                    evidence="No evidence collected yet",
                    needs=["Validated solutions", "Scientific evidence", "Natural approaches"],
                    pain_points=["Information quality", "Research validation", "Treatment efficacy"],
                    behaviors=["Research-focused", "Evidence-based decision making"]
                )
            ]
        ),
        Avatar(
            name="Active Manager",
            type="Avatar",
            insights=[
                AvatarInsight(
                    title="Activity Balance",
                    description="Analysis pending...",
                    evidence="No evidence collected yet",
                    needs=["Activity maintenance", "Pain management", "Recovery optimization"],
                    pain_points=["Activity limitations", "Recovery time", "Performance impact"],
                    behaviors=["Active lifestyle", "Adaptive exercise routines"]
                )
            ]
        )
    ])
    raw_perplexity_response: str = Field(default="")

class PerplexityParser:
    def __init__(self):
        logger.info("Initializing PerplexityParser")
        try:
            self.model = OpenAIModel('gpt-4o-mini')
            logger.info("OpenAI model initialized with gpt-4o-mini")
            
            self.agent = Agent[None, ParserResult](  # type: ignore
                model=self.model,
                result_type=ParserResult,
                system_prompt="""You are an insights parser that analyzes discussions and extracts structured information.
                
                For each analysis, you must provide:
                
                THREE INSIGHT SECTIONS:
                1. Pain & Frustration Analysis
                   - Identify key user complaints and pain points
                   - Extract emotional responses and frustrations
                   - Include supporting quotes as evidence
                
                2. Question & Advice Mapping
                   - Map frequently asked questions
                   - Identify suggested solutions and advice
                   - Include supporting quotes as evidence
                
                3. Pattern Detection
                   - Identify recurring themes and trends
                   - Note behavioral patterns
                   - Include supporting quotes as evidence
                
                THREE USER PERSONAS:
                - For each persona, identify:
                  - Demographic characteristics
                  - Key challenges and needs
                  - Pain points and frustrations
                  - Typical behaviors
                  - Supporting quotes as evidence
                
                REQUIREMENTS:
                - All insights must be evidence-based with supporting quotes
                - Each section must have at least one insight
                - Each persona must have complete details
                - Focus on actual patterns, not assumptions
                - Use clear, specific language""")
            logger.info("Pydantic AI agent initialized with system prompt")
        except Exception as e:
            logger.error(f"Error initializing PerplexityParser: {str(e)}", exc_info=True)
            raise

    async def parse_response(self, content: str, topic_keyword: str) -> ParserResult:
        """
        Parse the response using GPT-4o-mini to extract structured insights.
        """
        try:
            logger.info("Starting to parse response")
            result = await self.agent.run(f"""Analyze this discussion about {topic_keyword} and extract key insights:

Content to analyze:
{content}

Analyze the content to identify:
1. Pain & Frustration Analysis
   - Extract key complaints and emotional responses
   - Include direct quotes as evidence
   - Note significance of each insight

2. Question & Advice Mapping
   - Identify common questions and solutions
   - Include direct quotes as evidence
   - Note effectiveness of solutions

3. Pattern Detection
   - Identify behavioral and discussion patterns
   - Include direct quotes as evidence
   - Note correlations and trends

4. User Personas
   - Extract distinct user types from the discussion
   - Include characteristics, needs, and behaviors
   - Support with direct quotes
   - Note relative size and unique traits

Format each insight with:
- Clear title
- Supporting evidence (quotes)
- Significance or impact
- Source attribution

Use the actual content to identify natural groupings and patterns.""")
            
            if result is None or result.data is None:
                logger.warning("Received None response from agent")
                return ParserResult(raw_perplexity_response=content)
                
            parser_result = result.data
            parser_result.raw_perplexity_response = content

            # Ensure insights have proper structure
            for section in parser_result.sections:
                if not section.insights:
                    section.insights = [{
                        "title": f"No insights found for {section.title}",
                        "evidence": "Analysis pending...",
                        "source_url": None,
                        "engagement_metrics": None,
                        "frequency": None,
                        "correlation": None,
                        "significance": None
                    }]

            # Ensure avatars have proper structure
            for avatar in parser_result.avatars:
                if not avatar.insights:
                    avatar.insights = [
                        AvatarInsight(
                            title=f"No insights found for {avatar.name}",
                            description="Analysis pending...",
                            evidence="No evidence collected yet",
                            needs=["Needs analysis pending"],
                            pain_points=["Pain points analysis pending"],
                            behaviors=["Behaviors analysis pending"]
                        )
                    ]
            
            return parser_result
            
        except Exception as e:
            logger.error(f"Error in parse_response: {str(e)}", exc_info=True)
            return ParserResult(raw_perplexity_response=content) 