from typing import List
import logging
from .base_parser import BaseAnalysisParser
from .avatar_models import AvatarParserResult, AvatarInsight, AvatarProfile
from ....services.perplexity import PerplexityClient

logger = logging.getLogger(__name__)

class AvatarAnalysisParser(BaseAnalysisParser[AvatarParserResult]):
    def __init__(self):
        super().__init__(AvatarParserResult)
        self.perplexity = PerplexityClient()

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> AvatarParserResult:
        """Process the content and return structured avatar insights."""
        try:
            # Generate avatar insights using Perplexity
            response = await self.perplexity.generate_insights(
                content=content,
                topic_keyword=topic_keyword,
                section_type="avatar",
                user_query=user_query
            )

            # Parse the response into structured insights
            insights = []
            for item in response.get("insights", []):
                profile = AvatarProfile(
                    title=item.get("title", "Key Characteristics"),
                    description=item.get("description", ""),
                    evidence=item.get("evidence", ""),
                    query=user_query,
                    needs=item.get("needs", []),
                    pain_points=item.get("pain_points", []),
                    behaviors=item.get("behaviors", [])
                )

                avatar = AvatarInsight(
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    insights=[profile]
                )
                insights.append(avatar)

            return AvatarParserResult(insights=insights)

        except Exception as e:
            logger.error(f"Error processing avatar section: {str(e)}")
            return AvatarParserResult(insights=[]) 