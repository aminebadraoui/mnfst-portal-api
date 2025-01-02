from fastapi import APIRouter, HTTPException, Request
from uuid import UUID
from ..models.community_analysis import (
    AnalysisRequest,
    CommunityInsight,
    CommunityTrendsInput,
    CommunityTrendsResponse
)
from ..tasks import analyze_content_task, analyze_market_task
from ..celery_app import celery_app
from sse_starlette.sse import EventSourceResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze-insights")
async def analyze_insights(request: Request, analysis_request: AnalysisRequest):
    """Start background task to analyze community content from URLs."""
    try:
        # Log the incoming request
        logger.info(f"Received analysis request: {analysis_request.dict()}")
        
        # Convert research_id to UUID if it's a string
        research_id = str(UUID(str(analysis_request.research_id)))
        
        # Start Celery task
        task = analyze_content_task.delay(
            research_id=research_id,
            urls=analysis_request.urls
        )
        
        task_id = str(task.id)  # Convert UUID to string
        logger.info(f"Started Celery task {task_id} for research {research_id}")
        return {"task_id": task_id, "status": "started"}
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {str(e)}")
        raise HTTPException(status_code=422, detail="Invalid research ID format")
    except Exception as e:
        logger.error(f"Error starting analysis task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-trends")
async def analyze_trends_endpoint(data: CommunityTrendsInput):
    """Start background task to analyze market trends."""
    try:
        # Convert research_id to UUID if it's a string
        research_id = str(UUID(str(data.research_id)))
        
        # Start Celery task
        task = analyze_market_task.delay(
            research_id=research_id,
            insights=data.insights,
            quotes=data.quotes,
            keywords_found=data.keywords_found
        )
        
        task_id = str(task.id)  # Convert UUID to string
        logger.info(f"Started Celery task {task_id} for research {research_id}")
        return {"task_id": task_id, "status": "started"}
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {str(e)}")
        raise HTTPException(status_code=422, detail="Invalid research ID format")
    except Exception as e:
        logger.error(f"Error starting market analysis task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background task."""
    try:
        task = celery_app.AsyncResult(task_id)
        logger.info(f"Checking status for task {task_id}: {task.status}")
        
        if task.ready():
            try:
                result = task.get()
                logger.info(f"Task result: {result}")
                
                if isinstance(result, dict):
                    if result.get("status") == "completed":
                        return {
                            "status": "completed",
                            "insights_count": result.get("insights_count", 0),
                            "data": result.get("data", {})
                        }
                    elif result.get("status") == "failed":
                        return {
                            "status": "failed",
                            "error": result.get("error", "Task failed with no error message")
                        }
                
                # If result is not a dict or doesn't have status, treat as success
                return {
                    "status": "completed",
                    "data": result
                }
            except Exception as e:
                logger.error(f"Error getting task result: {str(e)}")
                return {
                    "status": "failed",
                    "error": str(e)
                }
        elif task.failed():
            error = str(task.result) if task.result else "Task failed with no error message"
            logger.error(f"Task failed: {error}")
            return {
                "status": "failed",
                "error": error
            }
        else:
            # Task is still processing
            progress = None
            if hasattr(task, 'info') and task.info:
                if isinstance(task.info, dict) and 'progress' in task.info:
                    progress = task.info['progress']
            
            return {
                "status": "processing",
                "progress": progress,
                "state": task.state
            }
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 