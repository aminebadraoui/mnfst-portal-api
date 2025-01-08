from typing import List
import logging
from .base_parser import BaseAnalysisParser
from .question_models import QuestionParserResult, QuestionInsight
from ....services.perplexity import PerplexityClient

logger = logging.getLogger(__name__)

class QuestionAnalysisParser(BaseAnalysisParser[QuestionParserResult]):
    def __init__(self):
        super().__init__(QuestionParserResult)
        self.perplexity = PerplexityClient()

    async def process_section(self, content: str, topic_keyword: str, user_query: str) -> QuestionParserResult:
        """Process the content and return structured question insights."""
        try:
            # Generate question insights using Perplexity
            response = await self.perplexity.generate_insights(
                content=content,
                topic_keyword=topic_keyword,
                section_type="question",
                user_query=user_query
            )

            # Parse the response into structured insights
            insights = []
            for item in response.get("insights", []):
                insight = QuestionInsight(
                    title=item.get("title", ""),
                    evidence=item.get("evidence", ""),
                    query=user_query,
                    source_url=item.get("source_url"),
                    engagement_metrics=item.get("engagement_metrics"),
                    frequency=item.get("frequency"),
                    correlation=item.get("correlation"),
                    significance=item.get("significance"),
                    question_type=item.get("question_type"),
                    suggested_answers=item.get("suggested_answers", []),
                    related_questions=item.get("related_questions", [])
                )
                insights.append(insight)

            return QuestionParserResult(insights=insights)

        except Exception as e:
            logger.error(f"Error processing question section: {str(e)}")
            return QuestionParserResult(insights=[]) 