from typing import List
import os
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from ..models.analysis import ChunkInsight

class ContentChunk(BaseModel):
    text: str
    chunk_number: int
    total_chunks: int
    source_url: str

class ChunkAnalysisResult(BaseModel):
    top_keyword: str
    key_insight: str
    key_quote: str

class ContentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        os.environ["OPENAI_API_KEY"] = self.api_key

        # Initialize the agent with a simpler prompt
        self.agent = Agent(
            'openai:gpt-4o-mini',
            result_type=ChunkAnalysisResult,
            deps_type=ContentChunk,
            system_prompt="""You are an expert marketing analyst. Your task is to analyze text and identify:
            1. The most significant keyword/phrase that represents a key topic or pain point
            2. The most important insight or takeaway that could be valuable for marketing
            3. A relevant verbatim quote that best illustrates the insight or pain point
            
            Focus on identifying actionable insights that could inform marketing strategies or product development.
            
            Respond with:
            - Top Keyword: [the most significant keyword or phrase]
            - Key Insight: [the most important insight or takeaway]
            - Key Quote: [a relevant verbatim quote]"""
        )

    async def analyze_chunk(self, chunk: ContentChunk) -> ChunkInsight:
        """Analyze a single chunk of content using pydantic-ai."""
        try:
            # Format the text with chunk information
            formatted_text = f"""Analyzing chunk {chunk.chunk_number} of {chunk.total_chunks}:
            ---
            {chunk.text}
            ---"""
            
            # Use the agent to analyze the chunk
            run_result = await self.agent.run(formatted_text)
            result = run_result.data

            return ChunkInsight(
                source=chunk.source_url,
                top_keyword=result.top_keyword,
                key_insight=result.key_insight,
                key_quote=result.key_quote
            )
        except Exception as e:
            print(f"Error analyzing chunk: {str(e)}")
            return ChunkInsight(
                source=chunk.source_url,
                top_keyword="Error analyzing content",
                key_insight="Error analyzing content",
                key_quote="Error analyzing content"
            )

    async def analyze_content(self, chunks: List[ContentChunk]) -> List[ChunkInsight]:
        """Analyze multiple chunks of content."""
        if not chunks or all(not chunk.text.strip() for chunk in chunks):
            return []

        insights = []
        for chunk in chunks:
            if chunk.text.strip():
                insight = await self.analyze_chunk(chunk)
                insights.append(insight)

        return insights 