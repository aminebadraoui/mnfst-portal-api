import logging
from typing import List
import os
from pydantic import BaseModel
from pydantic_ai import Agent
from ..models.analysis import MarketOpportunity

logger = logging.getLogger(__name__)

class MarketAnalysisChunk(BaseModel):
    keywords: List[str]
    insights: List[str]
    quotes: List[str]

class MarketAnalysisResult(BaseModel):
    opportunity: str
    pain_points: List[str]
    target_market: str
    potential_solutions: List[str]
    supporting_quotes: List[str]

class MarketAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        os.environ["OPENAI_API_KEY"] = self.api_key

        # Initialize the agent
        self.agent = Agent(
            'openai:gpt-4o-mini',
            result_type=MarketAnalysisResult,
            deps_type=MarketAnalysisChunk,
            system_prompt="""You are an expert market analyst and business strategist. Your task is to analyze the provided market research data and identify potential market opportunities and gaps.

For each chunk of data, analyze:
1. The key market opportunity or gap
2. The specific pain points that need to be addressed
3. The target market that would benefit most
4. Potential solutions or approaches to address the opportunity
5. Supporting quotes from the research that validate this opportunity

Focus on actionable insights that could lead to viable business opportunities.

Respond with:
- Opportunity: [describe the market opportunity or gap]
- Pain Points: [list the specific pain points]
- Target Market: [describe the ideal customer segment]
- Potential Solutions: [list potential approaches to address the opportunity]
- Supporting Quotes: [relevant quotes that validate this opportunity]"""
        )

    def chunk_data(self, keywords: List[str], insights: List[str], quotes: List[str], chunk_size: int = 3) -> List[MarketAnalysisChunk]:
        """Split the data into manageable chunks for analysis."""
        logger.info(f"Starting chunk_data with {len(keywords)} keywords, {len(insights)} insights, {len(quotes)} quotes")
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
            
            # Distribute keywords across chunks
            start_keyword_idx = (i * len(keywords)) // chunk_count
            end_keyword_idx = ((i + 1) * len(keywords)) // chunk_count
            chunk_keywords = keywords[start_keyword_idx:end_keyword_idx]
            
            logger.info(f"Creating chunk {i+1}/{chunk_count} with {len(chunk_keywords)} keywords, {len(chunk_insights)} insights")
            chunks.append(MarketAnalysisChunk(
                keywords=chunk_keywords,
                insights=chunk_insights,
                quotes=chunk_quotes
            ))
        
        logger.info(f"Returning {len(chunks)} chunks")
        return chunks

    async def analyze_chunk(self, chunk: MarketAnalysisChunk) -> MarketOpportunity:
        """Analyze a single chunk of market data."""
        try:
            logger.info(f"Analyzing chunk with {len(chunk.keywords)} keywords")
            # Format the data for analysis
            formatted_text = f"""Analyzing market research data:

Keywords identified:
{chr(10).join(f"- {k}" for k in chunk.keywords)}

Key insights:
{chr(10).join(f"- {i}" for i in chunk.insights)}

Supporting quotes:
{chr(10).join(f"- {q}" for q in chunk.quotes)}
"""
            logger.info("Sending chunk to agent for analysis")
            # Use the agent to analyze the chunk and get the data from RunResult
            run_result = await self.agent.run(formatted_text)
            result = run_result.data
            
            logger.info("Successfully analyzed chunk")
            return MarketOpportunity(
                opportunity=result.opportunity,
                pain_points=result.pain_points,
                target_market=result.target_market,
                potential_solutions=result.potential_solutions,
                supporting_quotes=result.supporting_quotes
            )
        except Exception as e:
            logger.error(f"Error analyzing market chunk: {str(e)}", exc_info=True)
            return MarketOpportunity(
                opportunity="Error analyzing market data",
                pain_points=["Error during analysis"],
                target_market="Unknown",
                potential_solutions=["Unable to determine solutions"],
                supporting_quotes=[]
            )

    async def analyze_market(self, keywords: List[str], insights: List[str], quotes: List[str], keywords_found: List[str] = None) -> List[MarketOpportunity]:
        """Analyze all market data and identify opportunities."""
        logger.info(f"Starting market analysis with: {len(keywords)} keywords, {len(insights)} insights, {len(quotes)} quotes")
        # Use keywords_found if keywords is empty
        effective_keywords = keywords if keywords else (keywords_found or [])
        logger.info(f"Using {len(effective_keywords)} effective keywords")
        
        if not effective_keywords or not insights or not quotes:
            logger.warning("Missing required data for analysis")
            return []

        chunks = self.chunk_data(effective_keywords, insights, quotes)
        opportunities = []

        logger.info(f"Processing {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}")
            opportunity = await self.analyze_chunk(chunk)
            opportunities.append(opportunity)
            logger.info(f"Added opportunity {i} to results")

        logger.info(f"Returning {len(opportunities)} opportunities")
        return opportunities 