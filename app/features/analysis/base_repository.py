from typing import Optional, List, Dict, Any, TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import json
from ....core.notifications import notify_insight_update, get_notification_connection

T = TypeVar('T')

logger = logging.getLogger(__name__)

class BaseAnalysisRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
        self.notification_conn = None

    async def init_notifications(self):
        """Initialize notification connection if needed."""
        if not self.notification_conn:
            self.notification_conn = await get_notification_connection()

    async def create_insight(
        self,
        user_id: str,
        project_id: str,
        query: str,
        task_id: str,
        insights: List[Dict[str, Any]] = None,
        raw_response: str = ""
    ) -> T:
        """Create a new insight."""
        logger.info(f"Creating insight for task {task_id}")
        
        insight = self.model_class(
            task_id=task_id,
            user_id=user_id,
            project_id=project_id,
            query=query,
            status="processing",
            insights=json.dumps(insights or []),
            raw_perplexity_response=raw_response
        )
        
        self.session.add(insight)
        await self.session.commit()
        
        try:
            await self.init_notifications()
            if self.notification_conn:
                await notify_insight_update(
                    self.notification_conn,
                    task_id=task_id,
                    project_id=project_id,
                    status="processing"
                )
        except Exception as e:
            logger.warning(f"Failed to send notification: {str(e)}")
        
        return insight

    async def update_insight(
        self,
        task_id: str,
        insights: List[Dict[str, Any]] = None,
        raw_response: str = None,
        error: str = None,
        status: str = None
    ) -> None:
        """Update an existing insight."""
        logger.info(f"Updating insight for task {task_id}")
        
        stmt = select(self.model_class).where(self.model_class.task_id == task_id)
        result = await self.session.execute(stmt)
        insight = result.scalar_one_or_none()
        
        if not insight:
            raise ValueError(f"No insight found for task_id: {task_id}")
        
        if insights is not None:
            insight.insights = json.dumps(insights)
        
        if raw_response is not None:
            insight.raw_perplexity_response = raw_response
        
        if error is not None:
            insight.error = error
            insight.status = "error"
        
        if status is not None:
            insight.status = status
        
        await self.session.commit()
        
        try:
            await self.init_notifications()
            if self.notification_conn:
                await notify_insight_update(
                    self.notification_conn,
                    task_id=task_id,
                    project_id=insight.project_id,
                    status=insight.status
                )
        except Exception as e:
            logger.warning(f"Failed to send notification: {str(e)}")

    async def get_insights(
        self,
        project_id: str,
        query: str = None,
        task_id: str = None
    ) -> Dict[str, Any]:
        """Get insights either by task ID or for a project."""
        logger.info(f"Getting insights - project: {project_id}, task: {task_id}, query: {query}")
        
        if task_id:
            # Case 1: Get specific insight by task_id (for polling)
            stmt = select(self.model_class).where(self.model_class.task_id == task_id)
            result = await self.session.execute(stmt)
            insight = result.scalar_one_or_none()
            
            if insight:
                try:
                    insights = json.loads(insight.insights) if isinstance(insight.insights, str) else insight.insights
                    return {
                        "status": insight.status,
                        "insights": insights or [],
                        "error": insight.error,
                        "raw_perplexity_response": insight.raw_perplexity_response
                    }
                except Exception as e:
                    logger.error(f"Error parsing insight data: {str(e)}")
                    return {
                        "status": insight.status,
                        "insights": [],
                        "error": str(e),
                        "raw_perplexity_response": insight.raw_perplexity_response
                    }
        else:
            # Case 2: Get all insights for project (for initial load)
            stmt = select(self.model_class).where(self.model_class.project_id == project_id)
            if query:
                stmt = stmt.where(self.model_class.query == query)
            result = await self.session.execute(stmt)
            insights = result.scalars().all()
            
            if not insights:
                return {
                    "status": "completed",
                    "insights": [],
                    "error": None,
                    "raw_perplexity_response": None
                }
            
            # Get overall status (processing if any insight is processing)
            status = "processing" if any(i.status == "processing" for i in insights) else "completed"
            error = next((i.error for i in insights if i.error), None)
            
            # Combine insights from all records
            all_insights = []
            raw_responses = []
            
            for insight in insights:
                try:
                    if insight.insights:
                        insights_data = json.loads(insight.insights) if isinstance(insight.insights, str) else insight.insights
                        all_insights.extend(insights_data)
                    
                    if insight.raw_perplexity_response:
                        raw_responses.append(insight.raw_perplexity_response)
                except Exception as e:
                    logger.error(f"Error processing insight {insight.task_id}: {str(e)}")
                    continue
            
            # Deduplicate insights
            unique_insights = {}
            for insight in all_insights:
                key = (insight.get("title", ""), insight.get("query", ""))
                if key not in unique_insights:
                    unique_insights[key] = insight
            
            return {
                "status": status,
                "insights": list(unique_insights.values()),
                "error": error,
                "raw_perplexity_response": "\n\n".join(raw_responses) if raw_responses else None
            }
        
        # Return empty state if no insight found
        return {
            "status": "processing",
            "insights": [],
            "error": None,
            "raw_perplexity_response": None
        } 