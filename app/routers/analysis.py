from fastapi import APIRouter, HTTPException
from typing import List
import logging
from fastapi.responses import StreamingResponse
import json
import asyncio
from ..models.analysis import AnalysisRequest, BatchAnalysisResponse, URLAnalysisResult
from ..services.scraper import process_url
from ..services.analyzer import ContentAnalyzer

router = APIRouter()
analyzer = ContentAnalyzer()
logger = logging.getLogger(__name__)

async def analysis_stream(request: AnalysisRequest):
    """Stream analysis results as they become available."""
    for url in request.urls:
        try:
            logger.info(f"Processing URL: {url}")
            # Send processing status
            yield f"data: {json.dumps({'type': 'status', 'message': f'Processing {str(url)}'})}\n\n"
            
            chunks = await process_url(str(url))
            if not chunks:
                logger.warning(f"No content could be extracted from {url}")
                yield f"data: {json.dumps({'type': 'error', 'url': str(url), 'error': 'No content could be extracted'})}\n\n"
                continue

            insights = []
            error_count = 0
            success = False
            
            # Process each chunk and send updates
            for i, chunk in enumerate(chunks, 1):
                try:
                    insight = await analyzer.analyze_chunk(chunk.text, i, len(chunks), url)
                    if insight:
                        # Convert insight to dict and ensure all HttpUrl objects are strings
                        insight_dict = {
                            'source': str(insight.source),
                            'top_keyword': insight.top_keyword,
                            'key_insight': insight.key_insight,
                            'key_quote': insight.key_quote
                        }
                        insights.append(insight_dict)
                        # Send chunk insight
                        yield f"data: {json.dumps({'type': 'chunk_insight', 'url': str(url), 'data': insight_dict})}\n\n"
                        success = True
                except Exception as e:
                    logger.error(f"Error analyzing chunk {i} from {url}: {str(e)}")
                    error_count += 1
                    if error_count >= 3:  # If we've had 3 consecutive errors, stop processing this URL
                        yield f"data: {json.dumps({'type': 'error', 'url': str(url), 'error': 'Too many analysis errors'})}\n\n"
                        break
                    continue

                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming the client
            
            # Only send URL completion if we had at least one successful insight
            if success:
                # Create result dictionary manually instead of using Pydantic model
                result = {
                    'url': str(url),
                    'insights': insights  # insights are already properly serialized
                }
                yield f"data: {json.dumps({'type': 'url_complete', 'data': result})}\n\n"
            
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            # Send error status
            yield f"data: {json.dumps({'type': 'error', 'url': str(url), 'error': str(e)})}\n\n"

@router.post("/analyze")
async def analyze_urls(request: AnalysisRequest):
    """Analyze URLs and stream results."""
    return StreamingResponse(
        analysis_stream(request),
        media_type="text/event-stream"
    ) 