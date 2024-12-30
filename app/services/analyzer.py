from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChunkContext:
    text: str
    chunk_number: int
    total_chunks: int
    word_count: int

class ChunkInsight(BaseModel):
    top_keyword: str = Field(description="The most frequently occurring or significant keyword/phrase in the chunk")
    key_insight: str = Field(description="The most important insight or takeaway from this chunk of text")
    key_quote: str = Field(description="A verbatim quote from the text that best represents the key insight or pain point")

class ContentAnalyzer:
    def __init__(self):
        logger.info("Initializing ContentAnalyzer")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        os.environ["OPENAI_API_KEY"] = api_key
        self.agent = Agent(
            'openai:gpt-4o-mini',
            result_type=ChunkInsight,
            deps_type=ChunkContext
        )
        logger.info("Agent initialized with model gpt-4o-mini")

        @self.agent.system_prompt
        def analyze_with_context(ctx: RunContext[ChunkContext]) -> str:
            return f"""You are an expert content analyzer. Analyzing chunk {ctx.deps.chunk_number} of {ctx.deps.total_chunks}.
            This chunk contains {ctx.deps.word_count} words.

            Here is the text to analyze:
            ---
            {ctx.deps.text}
            ---

            For this chunk of text:
            1. Identify the most significant or frequently used keyword/phrase
            2. Extract the most important insight or takeaway
            3. Select a verbatim quote that best represents the key insight or pain point (use exact words from the text)

            Focus on practical, actionable insights that could be valuable for marketing or business purposes.
            Consider how this chunk might relate to the overall content, given it's position ({ctx.deps.chunk_number}/{ctx.deps.total_chunks})."""

    async def analyze_chunk(self, text: str, chunk_number: int, total_chunks: int) -> ChunkInsight:
        """Analyze a single chunk of content."""
        logger.info(f"Analyzing chunk {chunk_number}/{total_chunks} (length: {len(text)} chars)")
        
        context = ChunkContext(
            text=text,
            chunk_number=chunk_number,
            total_chunks=total_chunks,
            word_count=len(text.split())
        )
        
        try:
            result = await self.agent.run(text, deps=context)
            logger.info(f"Analysis complete for chunk {chunk_number}. Result: {result.data}")
            return result.data
        except Exception as e:
            logger.error(f"Error analyzing chunk {chunk_number}: {str(e)}")
            raise

    async def analyze_content(self, chunks: List[str]) -> List[ChunkInsight]:
        """Analyze all content chunks."""
        logger.info(f"Starting analysis of {len(chunks)} chunks")
        insights = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{total_chunks}")
            insight = await self.analyze_chunk(chunk, i, total_chunks)
            insights.append(insight)
            
        logger.info("Content analysis complete")
        return insights 