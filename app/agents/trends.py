"""
Community Trends Agent

This module contains the agent that identifies patterns and trends across
community discussions, aggregating insights to understand common pain points
and potential solutions.
"""

import logging
from typing import List
from pydantic import BaseModel
from pydantic_ai import Agent
from ..models.community_analysis import CommunityTrend

logger = logging.getLogger(__name__)

# --- Models -------------------------------------------------------------------

class TrendAnalysisChunk(BaseModel):
    insights: List[str]
    quotes: List[str]

class TrendAnalysisResult(BaseModel):
    trend: str
    pain_points: List[str]
    affected_users: str
    potential_solutions: List[str]
    supporting_quotes: List[str]

# --- Agent Definition --------------------------------------------------------

agent = Agent(
    'openai:gpt-4o-mini',
    result_type=TrendAnalysisResult,
    deps_type=TrendAnalysisChunk,
    system_prompt="""You are an expert community researcher. Your task is to analyze aggregated community insights and identify:
    1. A significant trend or pattern in user problems/needs
    2. The specific pain points that make up this trend
    3. The type of users most affected by these problems
    4. Potential solutions that could address these needs
    5. Supporting quotes from the community that validate this trend

    Focus on identifying meaningful patterns that could inform product development or community support.

    Respond with:
    - Trend: [describe the significant pattern or theme]
    - Pain Points: [list the specific problems/challenges]
    - Affected Users: [describe who is most impacted]
    - Potential Solutions: [list possible ways to address the needs]
    - Supporting Quotes: [relevant quotes that validate this trend]"""
)

# --- Analysis Methods -------------------------------------------------------

def chunk_data(insights: List[str], quotes: List[str], chunk_size: int = 3) -> List[TrendAnalysisChunk]:
    """Split the data into manageable chunks for analysis."""
    logger.info(f"Starting chunk_data with {len(insights)} insights, {len(quotes)} quotes")
    chunks = []
    
    # Use the length of insights as the base for chunking since they're the main content
    total_items = len(insights)
    chunk_count = (total_items + chunk_size - 1) // chunk_size
    logger.info(f"Calculated chunk_count: {chunk_count} with chunk_size: {chunk_size}")
    
    for i in range(chunk_count):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_items)
        
        # Get corresponding slices for insights and quotes
        chunk_insights = insights[start_idx:end_idx]
        chunk_quotes = quotes[start_idx:end_idx]
        
        logger.info(f"Creating chunk {i+1}/{chunk_count} with {len(chunk_insights)} insights")
        chunks.append(TrendAnalysisChunk(
            insights=chunk_insights,
            quotes=chunk_quotes
        ))
    
    logger.info(f"Returning {len(chunks)} chunks")
    return chunks

async def analyze_chunk(chunk: TrendAnalysisChunk) -> CommunityTrend:
    """Analyze a single chunk of community data."""
    try:
        logger.info(f"Analyzing chunk with {len(chunk.insights)} insights")
        # Format the data for analysis
        formatted_text = f"""Analyzing community research data:

Key insights:
{chr(10).join(f"- {i}" for i in chunk.insights)}

Supporting quotes:
{chr(10).join(f"- {q}" for q in chunk.quotes)}
"""
        logger.info("Sending chunk to agent for analysis")
        # Use the agent to analyze the chunk
        run_result = await agent.run(formatted_text)
        result = run_result.data
        
        logger.info("Successfully analyzed chunk")
        return CommunityTrend(
            trend=result.trend,
            pain_points=result.pain_points,
            affected_users=result.affected_users,
            potential_solutions=result.potential_solutions,
            supporting_quotes=result.supporting_quotes
        )
    except Exception as e:
        logger.error(f"Error analyzing community chunk: {str(e)}", exc_info=True)
        return CommunityTrend(
            trend="Error analyzing community data",
            pain_points=["Error during analysis"],
            affected_users="Unknown",
            potential_solutions=["Unable to determine solutions"],
            supporting_quotes=[]
        )

async def analyze_trends(insights: List[str], quotes: List[str], keywords_found: List[str] = None) -> List[CommunityTrend]:
    """
    Analyze community research data to identify trends.
    
    Args:
        insights: List of key insights from content analysis
        quotes: List of relevant quotes
        keywords_found: Optional list of frequently mentioned keywords
    
    Returns:
        List of identified community trends
    """
    logger.info(f"Starting trends analysis with: {len(insights)} insights, {len(quotes)} quotes")
    
    if not insights or not quotes:
        logger.warning("Missing required data for analysis")
        return []

    chunks = chunk_data(insights, quotes)
    trends = []

    logger.info(f"Processing {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Processing chunk {i}/{len(chunks)}")
        trend = await analyze_chunk(chunk)
        trends.append(trend)
        logger.info(f"Added trend {i} to results")

    logger.info(f"Returning {len(trends)} trends")
    return trends 