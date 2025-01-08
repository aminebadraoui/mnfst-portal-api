from typing import List
import logging
from .base_parser import BaseAnalysisParser
from .pain_models import PainParserResult, PainInsight
from ....services.perplexity import PerplexityClient

logger = logging.getLogger(__name__)

class PainAnalysisParser(BaseAnalysisParser[PainParserResult]):
    def __init__(self):
        super().__init__(PainParserResult)
        self.perplexity = PerplexityClient()

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> PainParserResult:
        """Process the content and return structured pain insights."""
        try:
            # Generate pain insights using Perplexity
            response = await self.perplexity.generate_insights(
                content=content,
                topic_keyword=topic_keyword,
                section_type="pain",
                user_query=user_query
            )

            # Parse the response into structured insights
            insights = []
            for item in response.get("insights", []):
                insight = PainInsight(
                    title=item.get("title", ""),
                    evidence=item.get("evidence", ""),
                    query=user_query,
                    source_url=item.get("source_url"),
                    engagement_metrics=item.get("engagement_metrics"),
                    frequency=item.get("frequency"),
                    correlation=item.get("correlation"),
                    significance=item.get("significance"),
                    severity=item.get("severity"),
                    impact=item.get("impact"),
                    potential_solutions=item.get("potential_solutions", [])
                )
                insights.append(insight)

            return PainParserResult(insights=insights)

        except Exception as e:
            logger.error(f"Error processing pain section: {str(e)}")
            return PainParserResult(insights=[]) 