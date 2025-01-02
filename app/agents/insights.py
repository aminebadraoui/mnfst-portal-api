"""
Community Insights Agent

This module contains the agent that analyzes community discussions to identify
pain points, insights, and relevant quotes that help understand user needs and problems.
"""

import logging
from typing import List
from pydantic import BaseModel
from pydantic_ai import Agent
from ..models.community_analysis import CommunityInsight
from ..models.scraper import ContentChunk
import json

logger = logging.getLogger(__name__)

# --- Models -------------------------------------------------------------------

class CommunityAnalysisResult(BaseModel):
    pain_point: str
    key_insight: str
    supporting_quote: str

# --- Agent Definition --------------------------------------------------------

agent = Agent(
    'openai:gpt-4o-mini',
    result_type=CommunityAnalysisResult,
    deps_type=ContentChunk,
    system_prompt="""You are an expert community researcher. Your task is to analyze community discussions and identify:
    1. The most significant pain point or problem that community members are experiencing
    2. A key insight that helps understand the underlying needs or challenges
    3. A relevant verbatim quote that best illustrates the pain point or insight
    
    Focus on identifying real user problems and needs that could inform product development or solutions.
    
    Respond with:
    - Pain Point: [the most significant problem or challenge identified]
    - Key Insight: [an insight that helps understand the underlying need or context]
    - Supporting Quote: [a relevant verbatim quote from the community]"""
)

# --- Analysis Methods -------------------------------------------------------

async def analyze_chunk(chunk: ContentChunk) -> CommunityInsight:
    """Analyze a single chunk of community content."""
    try:
        logger.info(f"Starting analysis of chunk {chunk.chunk_number} of {chunk.total_chunks} from {chunk.source_url}")
        logger.debug(f"Chunk text length: {len(chunk.text)}")
        logger.debug(f"Chunk range: {chunk.start_index} to {chunk.end_index}")
        
        # Format the text with chunk information and metadata
        formatted_text = f"""Analyzing chunk {chunk.chunk_number} of {chunk.total_chunks}:
        Source: {chunk.source_url}
        Range: characters {chunk.start_index} to {chunk.end_index}
        ---
        {chunk.text}
        ---
        Additional metadata: {json.dumps(chunk.metadata) if chunk.metadata else 'None'}"""
        
        logger.info("Sending chunk to agent for analysis")
        logger.debug("Calling agent.run")
        run_result = await agent.run(formatted_text)
        logger.debug("Got result from agent")
        result = run_result.data
        logger.debug(f"Parsed result: {result}")

        logger.info("Successfully analyzed chunk")
        insight = CommunityInsight(
            source=chunk.source_url,
            pain_point=result.pain_point,
            key_insight=result.key_insight,
            supporting_quote=result.supporting_quote
        )
        logger.debug(f"Created CommunityInsight: {insight}")
        return insight
        
    except Exception as e:
        logger.error(f"Error analyzing chunk: {str(e)}", exc_info=True)
        return CommunityInsight(
            source=chunk.source_url,
            pain_point="Error analyzing content",
            key_insight="Error analyzing content",
            supporting_quote="Error analyzing content"
        )

async def analyze_community_content(chunks: List[ContentChunk]) -> List[CommunityInsight]:
    """Analyze multiple chunks of community content."""
    logger.info(f"Starting community content analysis with {len(chunks)} chunks")
    
    if not chunks or all(not chunk.text.strip() for chunk in chunks):
        logger.warning("No valid chunks to analyze")
        return []

    insights = []
    for i, chunk in enumerate(chunks, 1):
        if chunk.text.strip():
            logger.info(f"Processing chunk {i}/{len(chunks)}")
            logger.debug(f"Chunk text length: {len(chunk.text)}")
            insight = await analyze_chunk(chunk)
            insights.append(insight)
            logger.info(f"Added insight {i} from chunk")
            logger.debug(f"Insight {i}: {insight}")

    logger.info(f"Completed analysis, returning {len(insights)} insights")
    return insights 