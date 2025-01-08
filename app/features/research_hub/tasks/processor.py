import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_session
from ..perplexity.client import PerplexityClient
from ..parsers.base import BaseAnalysisParser
from ..repositories import (
    PainAnalysisRepository,
    QuestionAnalysisRepository,
    PatternAnalysisRepository,
    ProductAnalysisRepository,
    AvatarAnalysisRepository
)

logger = logging.getLogger(__name__)

async def process_analysis_task(
    task_id: str,
    user_id: str,
    project_id: str,
    topic_keyword: str,
    user_query: str,
    analysis_type: str,
    source_urls: List[str] = None,
    product_urls: List[str] = None,
    use_only_specified_sources: bool = False
) -> None:
    """Process an analysis task."""
    logger.info(f"Processing {analysis_type} analysis task {task_id}")
    
    # Map analysis types to their repositories
    repository_map = {
        "pain": PainAnalysisRepository,
        "question": QuestionAnalysisRepository,
        "pattern": PatternAnalysisRepository,
        "product": ProductAnalysisRepository,
        "avatar": AvatarAnalysisRepository
    }
    
    # Get the appropriate repository class
    repository_class = repository_map.get(analysis_type)
    if not repository_class:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
    
    # Initialize clients and repositories
    perplexity = PerplexityClient()
    async with get_session() as session:
        repository = repository_class(session)
        
        try:
            # Create initial insight record
            await repository.create_insight(
                user_id=user_id,
                project_id=project_id,
                query=user_query,
                task_id=task_id
            )
            
            # Generate insights using Perplexity
            content = await perplexity.generate_insights(
                topic_keyword=topic_keyword,
                user_query=user_query,
                section_type=analysis_type,
                source_urls=source_urls,
                product_urls=product_urls,
                use_only_specified_sources=use_only_specified_sources
            )
            
            # Parse insights using appropriate parser
            parser = BaseAnalysisParser()
            insights = await parser.process_section(
                content=content,
                section_type=analysis_type,
                topic_keyword=topic_keyword,
                user_query=user_query
            )
            
            # Update insight record with results
            await repository.update_insight(
                task_id=task_id,
                insights=insights,
                raw_response=content,
                status="completed"
            )
            
            logger.info(f"Completed {analysis_type} analysis task {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing {analysis_type} analysis task {task_id}: {str(e)}")
            await repository.update_insight(
                task_id=task_id,
                error=str(e),
                status="error"
            )
            raise 