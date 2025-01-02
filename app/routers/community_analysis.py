from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from typing import List, AsyncGenerator
import asyncio
import json
import logging
from starlette.responses import Response

from ..models.community_analysis import (
    AnalysisRequest, 
    CommunityInsight,
    CommunityTrendsInput,
    CommunityTrendsResponse
)
from ..services.scraper import scrape_and_chunk_content
from ..agents.insights import ContentChunk, analyze_chunk, analyze_community_content
from ..agents.trends import analyze_trends

logger = logging.getLogger(__name__)

router = APIRouter()

async def event_generator(request: Request, urls: List[str]) -> AsyncGenerator[ServerSentEvent, None]:
    """Generate events and handle client disconnection."""
    try:
        logger.info("Initializing analysis stream")
        # Send initial status
        yield ServerSentEvent(
            data=json.dumps({
                "type": "status",
                "message": "Starting community analysis..."
            })
        )
        await asyncio.sleep(0.1)  # Small delay to ensure proper streaming

        # Process each URL
        for url in urls:
            if await request.is_disconnected():
                logger.warning("Client disconnected, stopping stream")
                break

            logger.info(f"Processing URL: {url}")
            try:
                # Get content chunks
                logger.debug(f"Fetching and chunking content from {url}")
                chunks = await scrape_and_chunk_content(url)
                logger.info(f"Got {len(chunks)} chunks from {url}")
                
                if not chunks:
                    error_msg = f"No content found for URL {url}"
                    logger.warning(error_msg)
                    yield ServerSentEvent(
                        data=json.dumps({
                            "type": "error",
                            "error": error_msg
                        })
                    )
                    await asyncio.sleep(0.1)
                    continue
                
                # Analyze each chunk
                for i, chunk in enumerate(chunks, 1):
                    if await request.is_disconnected():
                        logger.warning("Client disconnected, stopping stream")
                        break

                    try:
                        logger.debug(f"Analyzing chunk {i}/{len(chunks)} from {url}")
                        logger.debug(f"Chunk content length: {len(chunk.text)}")
                        insight = await analyze_chunk(chunk)
                        logger.debug(f"Got insight for chunk {i}: {insight}")
                        
                        # Convert insight to dict and ensure all fields are present
                        insight_dict = {
                            "source": insight.source,
                            "pain_point": insight.pain_point,
                            "key_insight": insight.key_insight,
                            "supporting_quote": insight.supporting_quote
                        }
                        logger.debug(f"Converted insight to dict: {insight_dict}")
                        
                        yield ServerSentEvent(
                            data=json.dumps({
                                "type": "community_insight",
                                "data": insight_dict
                            })
                        )
                        await asyncio.sleep(0.1)  # Small delay between chunks
                        logger.info(f"Successfully sent insight for chunk {i} from {url}")
                        
                    except Exception as chunk_error:
                        error_msg = f"Error analyzing chunk {i}: {str(chunk_error)}"
                        logger.error(error_msg, exc_info=True)
                        yield ServerSentEvent(
                            data=json.dumps({
                                "type": "error",
                                "error": error_msg
                            })
                        )
                        await asyncio.sleep(0.1)

            except Exception as url_error:
                error_msg = f"Error processing URL {url}: {str(url_error)}"
                logger.error(error_msg, exc_info=True)
                yield ServerSentEvent(
                    data=json.dumps({
                        "type": "error",
                        "error": error_msg
                    })
                )
                await asyncio.sleep(0.1)

        if not await request.is_disconnected():
            logger.info("Analysis complete, sending final status")
            yield ServerSentEvent(
                data=json.dumps({
                    "type": "status",
                    "message": "Analysis complete"
                })
            )

    except Exception as e:
        error_msg = f"Stream error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if not await request.is_disconnected():
            yield ServerSentEvent(
                data=json.dumps({
                    "type": "error",
                    "error": error_msg
                })
            )

@router.post("/analyze-insights")
async def analyze_insights(request: Request, analysis_request: AnalysisRequest):
    """Analyze community content from URLs and stream insights."""
    logger.info(f"Starting insights analysis for URLs: {analysis_request.urls}")
    
    return EventSourceResponse(
        event_generator(request, analysis_request.urls),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # Disable buffering in nginx
        }
    )

@router.post("/analyze-trends")
async def analyze_trends_endpoint(data: CommunityTrendsInput) -> CommunityTrendsResponse:
    """Analyze community content and identify trends."""
    try:
        logger.info(f"Received trends analysis request with {len(data.insights)} insights, {len(data.quotes)} quotes, and {len(data.keywords_found)} keywords")
        logger.debug(f"Insights: {data.insights}")
        logger.debug(f"Quotes: {data.quotes}")
        logger.debug(f"Keywords: {data.keywords_found}")
        
        trends = await analyze_trends(
            insights=data.insights,
            quotes=data.quotes,
            keywords_found=data.keywords_found
        )
        
        logger.info(f"Analysis complete, found {len(trends)} trends")
        return CommunityTrendsResponse(trends=trends)
    except Exception as e:
        logger.error(f"Error in analyze_trends_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 