from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import asyncpg
import logging

from ....models.community_insight import CommunityInsight
from ....core.notifications import notify_insight_update, get_notification_connection
from ....core.database import get_db, AsyncSessionLocal
from ....models.user import User
from ....models.project import Project

logger = logging.getLogger(__name__)

class TaskRepository:
    def __init__(self):
        self.notification_conn: Optional[asyncpg.Connection] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def init_notifications(self):
        """Initialize notification connection if needed."""
        try:
            if not self.notification_conn:
                self.notification_conn = await get_notification_connection()
                logger.info("Successfully initialized notifications connection")
        except Exception as e:
            logger.warning(f"Failed to initialize notifications: {str(e)}")
            self.notification_conn = None  # Ensure it's None if initialization fails
            # Don't raise the error, just continue without notifications

    async def _get_session(self):
        """Get a database session."""
        session = AsyncSessionLocal()
        try:
            yield session
        finally:
            await session.close()

    async def create_task(self, task_id: str, user_id: str, project_id: str) -> None:
        """Create a new task."""
        logger.info(f"Creating task {task_id} for user {user_id} in project {project_id}")
        session = AsyncSessionLocal()
        try:
            insight = CommunityInsight(
                task_id=task_id,
                user_id=user_id,
                project_id=project_id,
                status="processing",
                sections=[],
                avatars=[]
            )
            session.add(insight)
            await session.commit()
            logger.info(f"Successfully created task {task_id}")

            # Try to initialize notifications, but don't let it block task creation
            try:
                await self.init_notifications()
            except Exception as e:
                logger.warning(f"Failed to initialize notifications during task creation: {str(e)}")
                # Continue without notifications
        except Exception as e:
            logger.error(f"Failed to create task {task_id}: {str(e)}", exc_info=True)
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def update_task(
        self,
        task_id: str,
        status: str,
        sections: List[Dict[str, Any]] = None,
        avatars: List[Dict[str, Any]] = None,
        error: str = None,
        raw_response: str = None
    ) -> None:
        """Update a task with results."""
        logger.info(f"Updating task {task_id} with status {status}")
        session = AsyncSessionLocal()
        try:
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await session.execute(stmt)
            insight = result.scalar_one_or_none()

            if not insight:
                logger.error(f"No insight found for task_id: {task_id}")
                raise ValueError(f"No insight found for task_id: {task_id}")

            insight.status = status
            if sections is not None:
                insight.sections = sections
                logger.debug(f"Updated sections for task {task_id}: {len(sections)} sections")
            if avatars is not None:
                insight.avatars = avatars
                logger.debug(f"Updated avatars for task {task_id}: {len(avatars)} avatars")
            if error is not None:
                insight.error = error
                logger.debug(f"Updated error for task {task_id}: {error}")
            if raw_response is not None:
                insight.raw_perplexity_response = raw_response
                logger.debug(f"Updated raw response for task {task_id}")

            await session.commit()
            logger.info(f"Successfully updated task {task_id}")

            # Try to send notification, but don't let it block the update
            try:
                if self.notification_conn:
                    # Send minimal notification data to avoid payload size limits
                    notification_data = {
                        "task_id": task_id,
                        "status": insight.status,
                        # Only send counts and status, not full data
                        "sections_count": len(insight.sections) if insight.sections else 0,
                        "avatars_count": len(insight.avatars) if insight.avatars else 0,
                        "has_error": bool(insight.error)
                    }
                    await notify_insight_update(self.notification_conn, task_id, notification_data)
                    logger.info(f"Sent notification for task {task_id}")
            except Exception as e:
                logger.warning(f"Failed to send notification for task {task_id}: {str(e)}")
                # Continue without notifications - don't let notification failures affect the update
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}", exc_info=True)
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def cleanup(self):
        """Cleanup resources."""
        if self.notification_conn:
            await self.notification_conn.close()
            self.notification_conn = None

class CommunityInsightRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_conn: Optional[asyncpg.Connection] = None

    async def init_notifications(self):
        """Initialize notification connection if needed."""
        try:
            if not self.notification_conn:
                self.notification_conn = await get_notification_connection()
                logger.info("Successfully initialized notifications connection")
        except Exception as e:
            logger.warning(f"Failed to initialize notifications: {str(e)}")
            self.notification_conn = None

    async def get_or_create_insight(
        self,
        user_id: str,
        project_id: str,
    ) -> CommunityInsight:
        """Get existing insight for project or create a new one."""
        # Try to get existing insight
        stmt = select(CommunityInsight).where(CommunityInsight.project_id == project_id)
        result = await self.session.execute(stmt)
        insight = result.scalar_one_or_none()

        if insight:
            logger.info(f"Found existing insight for project {project_id}")
            return insight

        # Create new insight if none exists
        logger.info(f"Creating new insight for project {project_id}")
        insight = CommunityInsight(
            user_id=user_id,
            project_id=project_id,
            sections=[],
            avatars=[]
        )
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def append_to_insight(
        self,
        project_id: str,
        new_sections: List[Dict[str, Any]] = None,
        new_avatars: List[Dict[str, Any]] = None,
        error: str = None,
        raw_response: str = None,
        notify: bool = True
    ) -> CommunityInsight:
        """Append new sections and avatars to existing insight."""
        stmt = select(CommunityInsight).where(CommunityInsight.project_id == project_id)
        result = await self.session.execute(stmt)
        insight = result.scalar_one_or_none()
        
        if not insight:
            raise ValueError(f"No insight found for project_id: {project_id}")

        # Append new sections if provided
        if new_sections:
            current_sections = insight.sections or []
            insight.sections = current_sections + new_sections

        # Append new avatars if provided
        if new_avatars:
            current_avatars = insight.avatars or []
            insight.avatars = current_avatars + new_avatars

        # Update other fields if provided
        if error is not None:
            insight.error = error
        if raw_response is not None:
            # Append to existing raw response
            current_response = insight.raw_perplexity_response or ""
            insight.raw_perplexity_response = current_response + "\n\n" + raw_response if current_response else raw_response

        await self.session.commit()
        await self.session.refresh(insight)

        # Send notification if requested
        if notify:
            try:
                await self.init_notifications()
                if self.notification_conn:
                    # Send minimal notification data
                    notification_data = {
                        "project_id": str(project_id),
                        "sections_count": len(insight.sections) if insight.sections else 0,
                        "avatars_count": len(insight.avatars) if insight.avatars else 0,
                        "has_error": bool(insight.error)
                    }
                    await notify_insight_update(self.notification_conn, str(project_id), notification_data)
                    logger.info(f"Sent notification for project {project_id}")
            except Exception as e:
                logger.warning(f"Failed to send notification for project {project_id}: {str(e)}")

        return insight

    async def get_project_insight(
        self,
        project_id: str
    ) -> Optional[CommunityInsight]:
        """Get insight for a project."""
        stmt = select(CommunityInsight).where(
            CommunityInsight.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def cleanup(self):
        """Cleanup resources."""
        if self.notification_conn:
            await self.notification_conn.close()
            self.notification_conn = None 