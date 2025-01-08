from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_session
from .services.analysis_service import AnalysisService
from .models.schemas.base import BaseAnalysisRequest, BaseAnalysisResponse
from .models.schemas.pain import PainAnalysisRequest, PainAnalysisResponse
from .models.schemas.question import QuestionAnalysisRequest, QuestionAnalysisResponse
from .models.schemas.pattern import PatternAnalysisRequest, PatternAnalysisResponse
from .models.schemas.product import ProductAnalysisRequest, ProductAnalysisResponse
from .models.schemas.avatar import AvatarAnalysisRequest, AvatarAnalysisResponse

router = APIRouter(prefix="/research-hub", tags=["Research Hub"])

@router.post("/pain-analysis", response_model=Dict[str, Any])
async def start_pain_analysis(
    request: PainAnalysisRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Start a pain analysis task."""
    service = AnalysisService(session)
    return await service.start_analysis(
        user_id=request.user_id,
        project_id=request.project_id,
        topic_keyword=request.topic_keyword,
        user_query=request.user_query,
        analysis_type="pain",
        source_urls=request.source_urls,
        product_urls=request.product_urls,
        use_only_specified_sources=request.use_only_specified_sources
    )

@router.post("/question-analysis", response_model=Dict[str, Any])
async def start_question_analysis(
    request: QuestionAnalysisRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Start a question analysis task."""
    service = AnalysisService(session)
    return await service.start_analysis(
        user_id=request.user_id,
        project_id=request.project_id,
        topic_keyword=request.topic_keyword,
        user_query=request.user_query,
        analysis_type="question",
        source_urls=request.source_urls,
        product_urls=request.product_urls,
        use_only_specified_sources=request.use_only_specified_sources
    )

@router.post("/pattern-analysis", response_model=Dict[str, Any])
async def start_pattern_analysis(
    request: PatternAnalysisRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Start a pattern analysis task."""
    service = AnalysisService(session)
    return await service.start_analysis(
        user_id=request.user_id,
        project_id=request.project_id,
        topic_keyword=request.topic_keyword,
        user_query=request.user_query,
        analysis_type="pattern",
        source_urls=request.source_urls,
        product_urls=request.product_urls,
        use_only_specified_sources=request.use_only_specified_sources
    )

@router.post("/product-analysis", response_model=Dict[str, Any])
async def start_product_analysis(
    request: ProductAnalysisRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Start a product analysis task."""
    service = AnalysisService(session)
    return await service.start_analysis(
        user_id=request.user_id,
        project_id=request.project_id,
        topic_keyword=request.topic_keyword,
        user_query=request.user_query,
        analysis_type="product",
        source_urls=request.source_urls,
        product_urls=request.product_urls,
        use_only_specified_sources=request.use_only_specified_sources
    )

@router.post("/avatar-analysis", response_model=Dict[str, Any])
async def start_avatar_analysis(
    request: AvatarAnalysisRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Start an avatar analysis task."""
    service = AnalysisService(session)
    return await service.start_analysis(
        user_id=request.user_id,
        project_id=request.project_id,
        topic_keyword=request.topic_keyword,
        user_query=request.user_query,
        analysis_type="avatar",
        source_urls=request.source_urls,
        product_urls=request.product_urls,
        use_only_specified_sources=request.use_only_specified_sources
    )

@router.get("/pain-analysis/{project_id}", response_model=PainAnalysisResponse)
async def get_pain_analysis(
    project_id: str,
    query: str = None,
    task_id: str = None,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get pain analysis results."""
    service = AnalysisService(session)
    return await service.get_analysis_results(
        project_id=project_id,
        analysis_type="pain",
        query=query,
        task_id=task_id
    )

@router.get("/question-analysis/{project_id}", response_model=QuestionAnalysisResponse)
async def get_question_analysis(
    project_id: str,
    query: str = None,
    task_id: str = None,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get question analysis results."""
    service = AnalysisService(session)
    return await service.get_analysis_results(
        project_id=project_id,
        analysis_type="question",
        query=query,
        task_id=task_id
    )

@router.get("/pattern-analysis/{project_id}", response_model=PatternAnalysisResponse)
async def get_pattern_analysis(
    project_id: str,
    query: str = None,
    task_id: str = None,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get pattern analysis results."""
    service = AnalysisService(session)
    return await service.get_analysis_results(
        project_id=project_id,
        analysis_type="pattern",
        query=query,
        task_id=task_id
    )

@router.get("/product-analysis/{project_id}", response_model=ProductAnalysisResponse)
async def get_product_analysis(
    project_id: str,
    query: str = None,
    task_id: str = None,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get product analysis results."""
    service = AnalysisService(session)
    return await service.get_analysis_results(
        project_id=project_id,
        analysis_type="product",
        query=query,
        task_id=task_id
    )

@router.get("/avatar-analysis/{project_id}", response_model=AvatarAnalysisResponse)
async def get_avatar_analysis(
    project_id: str,
    query: str = None,
    task_id: str = None,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get avatar analysis results."""
    service = AnalysisService(session)
    return await service.get_analysis_results(
        project_id=project_id,
        analysis_type="avatar",
        query=query,
        task_id=task_id
    ) 