from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.features.research_hub.query_generator import QueryGenerator, QueryGeneratorOutput
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI"])

class QueryGenerationRequest(BaseModel):
    description: str

@router.post("/generate-query", response_model=QueryGeneratorOutput)
async def generate_query(
    request: QueryGenerationRequest,
) -> QueryGeneratorOutput:
    """
    Generate a community-focused query based on project description using GPT-4.
    """
    try:
        generator = QueryGenerator()
        return await generator.generate(request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 