from typing import List
import os
from pydantic import BaseModel
from pydantic_ai import Agent
from ..models.analysis import MarketOpportunity

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

    def chunk_data(self, keywords: List[str], insights: List[str], quotes: List[str], chunk_size: int = 5) -> List[MarketAnalysisChunk]:
        """Split the data into manageable chunks for analysis."""
        chunks = []
        
        # Calculate how many items should be in each chunk
        total_items = len(keywords)
        chunk_count = (total_items + chunk_size - 1) // chunk_size
        
        for i in range(chunk_count):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_items)
            
            # Create corresponding slices for insights and quotes
            # Ensure we have matching insights and quotes for the keywords
            chunk_keywords = keywords[start_idx:end_idx]
            chunk_insights = insights[start_idx:end_idx] if start_idx < len(insights) else []
            chunk_quotes = quotes[start_idx:end_idx] if start_idx < len(quotes) else []
            
            chunks.append(MarketAnalysisChunk(
                keywords=chunk_keywords,
                insights=chunk_insights,
                quotes=chunk_quotes
            ))
        
        return chunks

    async def analyze_chunk(self, chunk: MarketAnalysisChunk) -> MarketOpportunity:
        """Analyze a single chunk of market data."""
        try:
            # Format the data for analysis
            formatted_text = f"""Analyzing market research data:

Keywords identified:
{chr(10).join(f"- {k}" for k in chunk.keywords)}

Key insights:
{chr(10).join(f"- {i}" for i in chunk.insights)}

Supporting quotes:
{chr(10).join(f"- {q}" for q in chunk.quotes)}
"""
            
            # Use the agent to analyze the chunk and get the data from RunResult
            run_result = await self.agent.run(formatted_text)
            result = run_result.data
            
            return MarketOpportunity(
                opportunity=result.opportunity,
                pain_points=result.pain_points,
                target_market=result.target_market,
                potential_solutions=result.potential_solutions,
                supporting_quotes=result.supporting_quotes
            )
        except Exception as e:
            print(f"Error analyzing market chunk: {str(e)}")
            return MarketOpportunity(
                opportunity="Error analyzing market data",
                pain_points=["Error during analysis"],
                target_market="Unknown",
                potential_solutions=["Unable to determine solutions"],
                supporting_quotes=[]
            )

    async def analyze_market(self, keywords: List[str], insights: List[str], quotes: List[str]) -> List[MarketOpportunity]:
        """Analyze all market data and identify opportunities."""
        if not keywords or not insights or not quotes:
            return []

        chunks = self.chunk_data(keywords, insights, quotes)
        opportunities = []

        for chunk in chunks:
            opportunity = await self.analyze_chunk(chunk)
            opportunities.append(opportunity)

        return opportunities 