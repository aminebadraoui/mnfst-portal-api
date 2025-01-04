from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import Message, MessageRole
from ..agents.perplexity_agent import (
    create_perplexity_agent,
    CompetitorAnalysis,
    MarketResearch,
    PerplexityResponse
)
from ..config import get_settings

router = APIRouter()
settings = get_settings()

class CompetitorAnalysisRequest(BaseModel):
    company_name: str
    industry: str
    specific_aspects: Optional[List[str]] = None

class MarketResearchRequest(BaseModel):
    topic: str
    focus_areas: List[str]

class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    model_name: str = "pplx-7b-online"

async def get_perplexity_agent() -> Agent:
    return create_perplexity_agent(api_key=settings.perplexity_api_key)

@router.post("/perplexity/analyze-competitors", response_model=PerplexityResponse)
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    agent: Agent = Depends(get_perplexity_agent)
):
    """
    Analyze competitors using the Perplexity AI model
    """
    try:
        task = CompetitorAnalysis(
            company_name=request.company_name,
            industry=request.industry,
            specific_aspects=request.specific_aspects or []
        )
        result = await agent.run(task)
        return PerplexityResponse(text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/perplexity/research-market", response_model=PerplexityResponse)
async def research_market(
    request: MarketResearchRequest,
    agent: Agent = Depends(get_perplexity_agent)
):
    """
    Conduct market research using the Perplexity AI model
    """
    try:
        task = MarketResearch(
            topic=request.topic,
            focus_areas=request.focus_areas
        )
        result = await agent.run(task)
        return PerplexityResponse(text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/perplexity/ask", response_model=PerplexityResponse)
async def ask_perplexity(
    request: QueryRequest,
    agent: Agent = Depends(get_perplexity_agent)
):
    """
    Send a direct query to the Perplexity AI model
    """
    try:
        messages = []
        if request.context:
            messages.append(Message(role=MessageRole.SYSTEM, content=request.context))
        messages.append(Message(role=MessageRole.USER, content=request.query))
        
        result = await agent.chat(messages)
        return PerplexityResponse(text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 