from typing import List, Optional, Literal, Dict, Type
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal
from app.features.research_hub.perplexity import get_client, CLIENT_MAP
from app.features.research_hub.models.schemas.base import BaseAnalysisRequest, BaseAnalysisResponse
from app.features.research_hub.models.database.pain_analysis import PainAnalysis
from app.features.research_hub.models.database.question_analysis import QuestionAnalysis
from app.features.research_hub.models.database.pattern_analysis import PatternAnalysis
from app.features.research_hub.models.database.product_analysis import ProductAnalysis
from app.features.research_hub.models.database.avatar_analysis import AvatarAnalysis
from app.features.research_hub.models.schemas.analysis_type import AnalysisTypeMetadata, ANALYSIS_TYPES_METADATA
from app.features.research_hub.repositories import create_repository
from app.features.research_hub.tasks.analysis import process_analysis
from app.features.research_hub.websockets.analysis import notification_manager
from app.core.auth import get_current_user, get_current_user_ws
from app.models.user import User
from app.models.project import Project
from app.core.rate_limit import rate_limit
import uuid
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# Create an enum for analysis types for better validation
class AnalysisType(str, Enum):
    PAIN = "Pain & Frustration Analysis"
    QUESTION = "Question & Advice Mapping"
    PATTERN = "Pattern Detection"
    PRODUCT = "Popular Products Analysis"
    AVATAR = "Avatars"

# Mapping of analysis types to their model classes
ANALYSIS_TYPE_TO_MODEL = {
    AnalysisType.PAIN: PainAnalysis,
    AnalysisType.QUESTION: QuestionAnalysis,
    AnalysisType.PATTERN: PatternAnalysis,
    AnalysisType.PRODUCT: ProductAnalysis,
    AnalysisType.AVATAR: AvatarAnalysis,
}

router = APIRouter(prefix="/research-hub", tags=["Research Hub"])

async def get_analysis_type(analysis_type: str = Path(...)) -> AnalysisType:
    """Custom dependency to validate and convert analysis type path parameter."""
    try:
        # Try to match the raw string to enum value
        return AnalysisType(analysis_type)
    except ValueError:
        # If direct match fails, try to find a matching enum value
        for enum_type in AnalysisType:
            if enum_type.value == analysis_type:
                return enum_type
        raise HTTPException(
            status_code=404,
            detail=f"Analysis type '{analysis_type}' not found. Available types: {[t.value for t in AnalysisType]}"
        )

@router.get("/analysis-types",
    response_model=Dict[str, AnalysisTypeMetadata],
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_analysis_types():
    """
    Get all available analysis types and their metadata.
    This endpoint is used to populate the UI with available analysis options.

    Returns:
    - Dictionary of analysis types with their metadata
    """
    try:
        return ANALYSIS_TYPES_METADATA
    except Exception as e:
        logger.error(f"Error fetching analysis types: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching analysis types"
        )

async def verify_project_access(
    project_id: str,
    current_user: User,
    session: AsyncSession
) -> Project:
    """Verify user has access to the project."""
    try:
        # Query the project
        project = await session.get(Project, uuid.UUID(project_id))
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check ownership
        if project.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this project"
            )
        
        return project
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")

@router.post("/{analysis_type}/analyze", 
    response_model=BaseAnalysisResponse,
    responses={
        400: {"description": "Invalid request parameters"},
        403: {"description": "Not authorized to access this project"},
        404: {"description": "Project not found or invalid analysis type"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(max_requests=10, window_seconds=60)
async def analyze_topic(
    analysis_type: AnalysisType = Depends(get_analysis_type),
    request: BaseAnalysisRequest = Body(..., description="Analysis request parameters"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> BaseAnalysisResponse:
    """
    Generate insights for a specific analysis type.

    Parameters:
    - analysis_type: Type of analysis (Pain & Frustration, Question & Advice, etc.)
    - request: Analysis request containing topic, query, and optional parameters
    - current_user: Authenticated user performing the analysis
    - session: Database session

    Returns:
    - BaseAnalysisResponse containing analysis results and metadata
    """
    try:
        # Verify project access
        await verify_project_access(request.project_id, current_user, session)

        # Get the appropriate model class for this analysis type
        model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
        
        # Create initial analysis record
        repository = create_repository(model_class)(session)
        analysis = await repository.create(
            user_id=current_user.id,
            project_id=request.project_id,
            query=request.user_query,
            insights={},  # Empty initially
            raw_perplexity_response="",  # Empty initially
            analysis_type=analysis_type.value
        )
        await session.commit()

        # Start Celery task
        process_analysis.delay(
            analysis_type=analysis_type.value,
            task_id=str(analysis.task_id),
            user_id=str(current_user.id),
            project_id=str(request.project_id),
            topic_keyword=request.topic_keyword,
            user_query=request.user_query,
            source_urls=request.source_urls,
            product_urls=request.product_urls,
            use_only_specified_sources=request.use_only_specified_sources
        )
        
        return BaseAnalysisResponse(
            id=analysis.id,
            task_id=analysis.task_id,
            status="processing",  # Initial status
            insights=[],  # Empty initially
            error=None
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_topic: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )

@router.get("/{analysis_type}/results/{task_id}",
    response_model=BaseAnalysisResponse,
    responses={
        400: {"description": "Invalid request parameters"},
        403: {"description": "Not authorized to access this analysis"},
        404: {"description": "Analysis not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_analysis_results(
    analysis_type: AnalysisType = Path(..., description="Type of analysis to retrieve"),
    task_id: str = Path(..., description="Task ID of the analysis"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> BaseAnalysisResponse:
    """
    Get the results of a specific analysis task.

    Parameters:
    - analysis_type: Type of analysis (Pain & Frustration, Question & Advice, etc.)
    - task_id: Unique identifier of the analysis task
    - current_user: Authenticated user requesting the results
    - session: Database session

    Returns:
    - BaseAnalysisResponse containing analysis results and metadata
    """
    try:
        # Validate task_id format
        try:
            uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task ID format")

        # Get the appropriate model class for this analysis type
        model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
        
        # Create repository for the analysis type
        repository = create_repository(model_class)(session)
        
        # Get analysis from database
        analysis = await repository.get_by_task_id(task_id, analysis_type.value)
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis with task ID {task_id} not found"
            )
            
        # Check ownership
        if analysis.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this analysis"
            )
            
        return BaseAnalysisResponse(
            id=analysis.id,
            task_id=analysis.task_id,
            status=analysis.status,
            insights=analysis.insights.get("insights", []) if analysis.insights else [],
            error=analysis.error
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_analysis_results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the analysis"
        )

@router.get("/{analysis_type}/project/{project_id}",
    response_model=List[BaseAnalysisResponse],
    responses={
        400: {"description": "Invalid request parameters"},
        403: {"description": "Not authorized to access this project"},
        404: {"description": "Project not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_project_analyses(
    analysis_type: AnalysisType = Path(..., description="Type of analysis to list"),
    project_id: str = Path(..., description="Project ID to get analyses for"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
) -> List[BaseAnalysisResponse]:
    """
    Get all analyses for a specific project.

    Parameters:
    - analysis_type: Type of analysis (Pain & Frustration, Question & Advice, etc.)
    - project_id: ID of the project to get analyses for
    - current_user: Authenticated user requesting the analyses
    - session: Database session
    - limit: Maximum number of results to return (1-100)
    - offset: Number of results to skip for pagination

    Returns:
    - List of BaseAnalysisResponse containing analysis results and metadata
    """
    try:
        # Verify project access
        await verify_project_access(project_id, current_user, session)

        # Get the appropriate model class for this analysis type
        model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
        
        # Create repository for the analysis type
        repository = create_repository(model_class)(session)
        
        # Get analyses from database
        analyses = await repository.get_by_project(
            project_id=project_id,
            user_id=current_user.id,
            analysis_type=analysis_type.value,
            limit=limit,
            offset=offset
        )
        
        return [
            BaseAnalysisResponse(
                id=analysis.id,
                task_id=analysis.task_id,
                status=analysis.status,
                insights=analysis.insights.get("insights", []) if analysis.insights else [],
                error=analysis.error
            )
            for analysis in analyses
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_project_analyses: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the analyses"
        )

@router.websocket("/{analysis_type}/ws/{task_id}")
async def analysis_websocket(
    websocket: WebSocket,
    analysis_type: AnalysisType,
    task_id: str,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time analysis updates.
    """
    try:
        # Validate task_id format
        try:
            uuid.UUID(task_id)
        except ValueError:
            await websocket.close(code=4000, reason="Invalid task ID format")
            return

        # Verify access to the analysis
        async with AsyncSessionLocal() as session:
            repository = create_repository(ANALYSIS_TYPE_TO_MODEL[analysis_type])(session)
            analysis = await repository.get_by_task_id(task_id, analysis_type.value)
            
            if not analysis:
                await websocket.close(code=4004, reason="Analysis not found")
                return
                
            if analysis.user_id != current_user.id:
                await websocket.close(code=4003, reason="Not authorized to access this analysis")
                return

        # Connect to WebSocket
        await notification_manager.connect(websocket, task_id)
        
        try:
            while True:
                # Keep connection alive and handle client messages if needed
                data = await websocket.receive_text()
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            notification_manager.disconnect(websocket, task_id)
            
    except Exception as e:
        logger.error(f"Error in analysis websocket: {str(e)}")
        await websocket.close(code=4500, reason="Internal server error") 

@router.post("/analyze-all", 
    response_model=Dict[str, BaseAnalysisResponse],
    responses={
        400: {"description": "Invalid request parameters"},
        403: {"description": "Not authorized to access this project"},
        404: {"description": "Project not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(max_requests=10, window_seconds=60)
async def analyze_all(
    request: BaseAnalysisRequest = Body(..., description="Analysis request parameters"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, BaseAnalysisResponse]:
    """
    Generate insights for all analysis types in parallel.

    Parameters:
    - request: Analysis request containing topic, query, and optional parameters
    - current_user: Authenticated user performing the analysis
    - session: Database session

    Returns:
    - Dictionary mapping analysis types to their BaseAnalysisResponse
    """
    try:
        # Verify project access
        await verify_project_access(request.project_id, current_user, session)

        responses = {}
        
        # Create analysis records and start tasks for each analysis type
        for analysis_type in AnalysisType:
            # Get the appropriate model class for this analysis type
            model_class = ANALYSIS_TYPE_TO_MODEL[analysis_type]
            
            # Create initial analysis record
            repository = create_repository(model_class)(session)
            analysis = await repository.create(
                user_id=current_user.id,
                project_id=request.project_id,
                query=request.user_query,
                insights={},  # Empty initially
                raw_perplexity_response="",  # Empty initially
                analysis_type=analysis_type.value
            )

            # Start Celery task
            process_analysis.delay(
                analysis_type=analysis_type.value,
                task_id=str(analysis.task_id),
                user_id=str(current_user.id),
                project_id=str(request.project_id),
                topic_keyword=request.topic_keyword,
                user_query=request.user_query,
                source_urls=request.source_urls,
                product_urls=request.product_urls,
                use_only_specified_sources=request.use_only_specified_sources
            )
            
            responses[analysis_type.value] = BaseAnalysisResponse(
                id=analysis.id,
                task_id=analysis.task_id,
                status="processing",  # Initial status
                insights=[],  # Empty initially
                error=None
            )
        
        await session.commit()
        return responses

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_all: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        ) 

@router.get("/project/{project_id}/queries", response_model=List[str])
async def get_project_queries(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> List[str]:
    """
    Get all unique queries for a project's research analyses.
    """
    try:
        # Verify project access
        await verify_project_access(project_id, current_user, session)
        
        # Get unique queries from all analysis types
        all_queries = set()
        for model_class in ANALYSIS_TYPE_TO_MODEL.values():
            repository = create_repository(model_class)(session)
            queries = await repository.get_project_queries(project_id)
            all_queries.update(queries)
        
        return sorted(list(all_queries))
    except Exception as e:
        logger.error(f"Error getting project queries: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the queries"
        ) 