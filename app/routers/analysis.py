from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.analysis import AnalysisRequest, AnalysisResponse, RelevantQuote
from ..services.scraper import process_url
from ..services.analyzer import ContentAnalyzer
import logging
import json
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()
analyzer = ContentAnalyzer()

async def generate_analysis_events(chunks):
    """Generate SSE events for each analyzed chunk."""
    try:
        total_chunks = len(chunks)
        logger.info(f"Starting analysis stream for {total_chunks} chunks")
        
        for i, chunk in enumerate(chunks, 1):
            insight = await analyzer.analyze_chunk(chunk.text, i, total_chunks)
            
            # Create event data
            event_data = {
                "type": "chunk_insight",
                "data": {
                    "chunk_number": i,
                    "total_chunks": total_chunks,
                    "insight": {
                        "top_keyword": insight.top_keyword,
                        "key_insight": insight.key_insight,
                        "key_quote": insight.key_quote
                    }
                }
            }
            
            # Yield SSE formatted event
            yield f"data: {json.dumps(event_data)}\n\n"
            
        # Send completion event
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in analysis stream: {str(e)}")
        error_data = {
            "type": "error",
            "data": {"message": str(e)}
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@router.post("/analyze")
async def analyze_url(request: AnalysisRequest):
    """Analyze a URL and stream the results."""
    try:
        # Process the URL and get content chunks
        chunks = await process_url(str(request.url))
        logger.info(f"Number of chunks extracted: {len(chunks)}")
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the URL"
            )

        return StreamingResponse(
            generate_analysis_events(chunks),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing URL: {str(e)}"
        ) 