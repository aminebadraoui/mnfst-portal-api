from typing import List
import logging
from .base_parser import BaseAnalysisParser
from .product_models import ProductParserResult, ProductInsight
from ....services.perplexity import PerplexityClient

logger = logging.getLogger(__name__)

class ProductAnalysisParser(BaseAnalysisParser[ProductParserResult]):
    def __init__(self):
        super().__init__(ProductParserResult)
        self.perplexity = PerplexityClient()

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> ProductParserResult:
        """Process the content and return structured product insights."""
        try:
            # Generate product insights using Perplexity
            response = await self.perplexity.generate_insights(
                content=content,
                topic_keyword=topic_keyword,
                section_type="product",
                user_query=user_query
            )

            # Parse the response into structured insights
            insights = []
            for item in response.get("insights", []):
                insight = ProductInsight(
                    title=item.get("title", ""),
                    evidence=item.get("evidence", ""),
                    query=user_query,
                    source_url=item.get("source_url"),
                    engagement_metrics=item.get("engagement_metrics"),
                    frequency=item.get("frequency"),
                    correlation=item.get("correlation"),
                    significance=item.get("significance"),
                    platform=item.get("platform", ""),
                    price_range=item.get("price_range"),
                    positive_feedback=item.get("positive_feedback", []),
                    negative_feedback=item.get("negative_feedback", []),
                    market_gap=item.get("market_gap")
                )
                insights.append(insight)

            return ProductParserResult(insights=insights)

        except Exception as e:
            logger.error(f"Error processing product section: {str(e)}")
            return ProductParserResult(insights=[]) 