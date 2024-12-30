from typing import List
from pydantic import BaseModel, Field, HttpUrl
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import os
import logging
from dotenv import load_dotenv
from ..models.scraper import ContentChunk
import openai

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
    source_url: HttpUrl

class ChunkInsight(BaseModel):
    source: HttpUrl = Field(description="The URL this insight was extracted from")
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

    async def analyze_chunk(self, text: str, chunk_number: int, total_chunks: int, source_url: HttpUrl) -> ChunkInsight:
        """Analyze a single chunk of content."""
        try:
            logger.info(f"Analyzing chunk {chunk_number}/{total_chunks} (length: {len(text)} chars)")
            
            messages = [
                {"role": "system", "content": "You are an expert marketing analyst. Extract key insights from the provided content."},
                {"role": "user", "content": f"Analyze this content and extract:\n1. The most significant keyword/phrase\n2. A key insight or takeaway\n3. A relevant verbatim quote\n\nContent:\n{text}"}
            ]
            
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse the response into structured data
            lines = content.strip().split('\n')
            keyword = ""
            insight = ""
            quote = ""
            
            for line in lines:
                if line.startswith("1."):
                    keyword = line[2:].strip()
                elif line.startswith("2."):
                    insight = line[2:].strip()
                elif line.startswith("3."):
                    quote = line[2:].strip()
            
            return ChunkInsight(
                source=source_url,
                top_keyword=keyword or "No keyword found",
                key_insight=insight or "No insight found",
                key_quote=quote or "No quote found"
            )
            
        except Exception as e:
            logger.error(f"Error analyzing chunk {chunk_number}: {str(e)}")
            # Return a default insight instead of raising an error
            return ChunkInsight(
                source=source_url,
                top_keyword="Error occurred",
                key_insight=f"Failed to analyze chunk {chunk_number}",
                key_quote="No quote available"
            )

    async def analyze_content(self, chunks: List[ContentChunk], source_url: HttpUrl) -> List[ChunkInsight]:
        """Analyze all content chunks."""
        logger.info(f"Starting analysis of {len(chunks)} chunks from {source_url}")
        insights = []
        total_chunks = len(chunks)
        
        # If no chunks or all chunks are empty, return empty list
        if not chunks or all(not chunk.text.strip() for chunk in chunks):
            logger.warning("No valid content to analyze")
            return []
        
        for i, chunk in enumerate(chunks, 1):
            if not chunk.text.strip():
                continue
                
            try:
                logger.info(f"Processing chunk {i}/{total_chunks}")
                insight = await self.analyze_chunk(chunk.text, i, total_chunks, source_url)
                if insight:  # Only add non-None insights
                    insights.append(insight)
            except Exception as e:
                logger.error(f"Error analyzing chunk {i}: {str(e)}")
                # Continue with next chunk instead of failing the entire analysis
                continue
            
        logger.info("Content analysis complete")
        return insights  # Return collected insights, empty list if none were successful 