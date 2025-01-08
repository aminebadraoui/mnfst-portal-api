from typing import List
import logging
from .base_parser import BaseAnalysisParser
from .pattern_models import PatternParserResult, PatternInsight
from ....services.perplexity import PerplexityClient

logger = logging.getLogger(__name__)

class PatternAnalysisParser(BaseAnalysisParser[PatternParserResult]):
    def __init__(self):
        super().__init__(PatternParserResult)
        self.perplexity = PerplexityClient()

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> PatternParserResult:
        """Process the content and return structured pattern insights."""
        try:
            # Generate pattern insights using Perplexity
            response = await self.perplexity.generate_insights(
                content=content,
                topic_keyword=topic_keyword,
                section_type="pattern",
                user_query=user_query
            )

            # Parse the response into structured insights
            insights = []
            for item in response.get("insights", []):
                insight = PatternInsight(
                    title=item.get("title", ""),
                    evidence=item.get("evidence", ""),
                    query=user_query,
                    source_url=item.get("source_url"),
                    engagement_metrics=item.get("engagement_metrics"),
                    frequency=item.get("frequency"),
                    correlation=item.get("correlation"),
                    significance=item.get("significance"),
                    pattern_type=item.get("pattern_type"),
                    trend_direction=item.get("trend_direction"),
                    supporting_data=item.get("supporting_data", []),
                    implications=item.get("implications", [])
                )
                insights.append(insight)

            return PatternParserResult(insights=insights)

        except Exception as e:
            logger.error(f"Error processing pattern section: {str(e)}")
            return PatternParserResult(insights=[]) 