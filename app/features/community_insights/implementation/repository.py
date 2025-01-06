from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import asyncpg
import logging
import asyncio
import json

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
        try:
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            insight = result.scalar_one_or_none()

            if not insight:
                logger.error(f"No insight found for task_id: {task_id}")
                raise ValueError(f"No insight found for task_id: {task_id}")

            # Log current state
            logger.info(f"Current sections: {json.dumps(insight.sections, indent=2) if insight.sections else '[]'}")
            logger.info(f"New sections to save: {json.dumps(sections, indent=2) if sections else '[]'}")

            insight.status = status
            if sections is not None:
                insight.sections = sections
                logger.info(f"Updated sections for task {task_id}: {len(sections)} sections")
            if avatars is not None:
                insight.avatars = avatars
                logger.info(f"Updated avatars for task {task_id}: {len(avatars)} avatars")
            if error is not None:
                insight.error = error
                logger.info(f"Updated error for task {task_id}: {error}")
            if raw_response is not None:
                if insight.raw_perplexity_response:
                    insight.raw_perplexity_response += "\n\n" + raw_response
                else:
                    insight.raw_perplexity_response = raw_response
                logger.info(f"Updated raw response for task {task_id}")

            await self.session.commit()
            
            # Verify the update
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            updated_insight = result.scalar_one_or_none()
            
            if not updated_insight:
                raise ValueError(f"Failed to verify update - insight not found after commit")
                
            logger.info(f"Verified sections after update: {json.dumps(updated_insight.sections, indent=2) if updated_insight.sections else '[]'}")
            logger.info(f"Successfully updated task {task_id}")

        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise

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
        query: str = None,
    ) -> CommunityInsight:
        """Get existing insight for project and query or create a new one."""
        # Try to get existing insight for this project and query
        stmt = select(CommunityInsight).where(
            CommunityInsight.project_id == project_id,
            CommunityInsight.query == query
        )
        result = await self.session.execute(stmt)
        insight = result.scalar_one_or_none()

        if insight:
            logger.info(f"Found existing insight for project {project_id} and query {query}")
            # Set status back to processing for new task
            insight.status = "processing"
            await self.session.commit()
            return insight

        # Create new insight with predefined empty sections
        logger.info(f"Creating new insight for project {project_id} and query {query}")
        empty_sections = [
            {
                "title": "Pain & Frustration Analysis",
                "icon": "FaExclamationCircle",
                "insights": []
            },
            {
                "title": "Failed Solutions Analysis",
                "icon": "FaTimesCircle",
                "insights": []
            },
            {
                "title": "Question & Advice Mapping",
                "icon": "FaQuestionCircle",
                "insights": []
            },
            {
                "title": "Pattern Detection",
                "icon": "FaChartLine",
                "insights": []
            },
            {
                "title": "Popular Products Analysis",
                "icon": "FaShoppingCart",
                "insights": []
            }
        ]
        insight = CommunityInsight(
            user_id=user_id,
            project_id=project_id,
            query=query,
            sections=empty_sections,
            avatars=[],
            status="processing"  # Set initial status to processing
        )
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def get_project_insights(
        self,
        project_id: str,
        query: str = None
    ) -> List[CommunityInsight]:
        """Get all insights for a project, optionally filtered by query."""
        try:
            stmt = select(CommunityInsight).where(CommunityInsight.project_id == project_id)
            if query:
                stmt = stmt.where(CommunityInsight.query == query)
            
            # Set a timeout for the database operation
            async with asyncio.timeout(5.0):  # 5 second timeout
                result = await self.session.execute(stmt)
                return result.scalars().all()
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout getting insights for project {project_id}", exc_info=True)
            raise TimeoutError("Database operation timed out") from e
        except Exception as e:
            logger.error(f"Error getting insights for project {project_id}: {str(e)}", exc_info=True)
            raise

    async def append_to_insight(
        self,
        task_id: str,
        new_sections: List[Dict[str, Any]] = None,
        new_avatars: List[Dict[str, Any]] = None,
        raw_response: str = None,
        error: str = None
    ) -> None:
        """Append new sections or avatars to an insight."""
        logger.info(f"Appending to insight for task {task_id}")
        try:
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            insight = result.scalar_one_or_none()

            if not insight:
                logger.error(f"No insight found for task_id: {task_id}")
                raise ValueError(f"No insight found for task_id: {task_id}")

            if new_sections:
                logger.info(f"Updating sections for task {task_id}")
                try:
                    current_sections = insight.sections or []
                    logger.info(f"Current sections loaded: {json.dumps(current_sections, indent=2)}")
                except Exception as e:
                    logger.warning(f"Failed to parse current sections, starting fresh: {str(e)}")
                    current_sections = []

                # For each new section
                for new_section in new_sections:
                    # Handle case where new_section might be a string
                    if isinstance(new_section, str):
                        logger.warning(f"Received string section instead of dict: {new_section}")
                        continue
                        
                    # Find matching section by title
                    matching_section = next(
                        (section for section in current_sections 
                         if section["title"] == new_section["title"]),
                        None
                    )
                    
                    if matching_section:
                        # Update existing section with new insights
                        logger.info(f"Updating existing section: {new_section['title']}")
                        matching_section["insights"] = new_section["insights"]
                        logger.info(f"Updated insights count: {len(new_section['insights'])}")
                    else:
                        # Add new section if no match found
                        logger.info(f"Adding new section: {new_section['title']}")
                        current_sections.append(new_section)

                insight.sections = current_sections

            if new_avatars:
                logger.info(f"Updating avatars for task {task_id}")
                try:
                    # Ensure new_avatars is a list
                    if not isinstance(new_avatars, list):
                        logger.warning(f"new_avatars is not a list, converting: {type(new_avatars)}")
                        new_avatars = [new_avatars] if new_avatars else []

                    # Validate and clean avatar data
                    validated_avatars = []
                    for avatar in new_avatars:
                        try:
                            # Convert string to dict if needed
                            if isinstance(avatar, str):
                                avatar = json.loads(avatar)
                            
                            if not isinstance(avatar, dict):
                                logger.warning(f"Invalid avatar format, skipping: {avatar}")
                                continue
                                
                            if not all(key in avatar for key in ["name", "type", "insights"]):
                                logger.warning(f"Avatar missing required fields, skipping: {avatar}")
                                continue
                                
                            # Ensure insights is a list
                            if not isinstance(avatar["insights"], list):
                                logger.warning(f"Avatar insights is not a list, skipping: {avatar}")
                                continue
                                
                            # Clean and validate each insight
                            cleaned_insights = []
                            for insight in avatar["insights"]:
                                if not isinstance(insight, dict):
                                    try:
                                        insight = json.loads(insight) if isinstance(insight, str) else {}
                                    except:
                                        continue
                                        
                                cleaned_insight = {
                                    "title": str(insight.get("title", "")),
                                    "description": str(insight.get("description", "")),
                                    "evidence": str(insight.get("evidence", "")),
                                    "query": str(insight.get("query", "")),
                                    "needs": insight.get("needs", []) if isinstance(insight.get("needs"), list) else [],
                                    "pain_points": insight.get("pain_points", []) if isinstance(insight.get("pain_points"), list) else [],
                                    "behaviors": insight.get("behaviors", []) if isinstance(insight.get("behaviors"), list) else []
                                }
                                cleaned_insights.append(cleaned_insight)
                                
                            cleaned_avatar = {
                                "name": str(avatar["name"]),
                                "type": str(avatar["type"]),
                                "insights": cleaned_insights
                            }
                            validated_avatars.append(cleaned_avatar)
                            
                        except Exception as e:
                            logger.error(f"Error processing avatar: {str(e)}", exc_info=True)
                            continue

                    insight.avatars = validated_avatars
                    logger.info(f"Successfully updated avatars: {len(validated_avatars)} avatars")
                    logger.debug(f"Validated avatars: {json.dumps(validated_avatars, indent=2)}")
                except Exception as e:
                    logger.error(f"Error processing avatars: {str(e)}", exc_info=True)
                    raise

            if raw_response:
                if insight.raw_perplexity_response:
                    insight.raw_perplexity_response += "\n\n" + raw_response
                else:
                    insight.raw_perplexity_response = raw_response

            if error:
                insight.error = error

            # Update status to completed
            insight.status = "completed"
            logger.info(f"Updated status to completed for task {task_id}")

            await self.session.commit()
            
            # Verify the save
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            saved_insight = result.scalar_one_or_none()
            
            if not saved_insight:
                raise ValueError("Failed to verify save - insight not found after commit")
                
            logger.info(f"Successfully saved insight with {len(saved_insight.sections)} sections and {len(saved_insight.avatars)} avatars")

        except Exception as e:
            logger.error(f"Failed to append to insight: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise

    async def get_project_insight(
        self,
        project_id: str,
        query: str = None
    ) -> Optional[CommunityInsight]:
        """Get insight for a project and query."""
        stmt = select(CommunityInsight).where(
            CommunityInsight.project_id == project_id
        )
        if query:
            stmt = stmt.where(CommunityInsight.query == query)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def cleanup(self):
        """Cleanup resources."""
        if self.notification_conn:
            await self.notification_conn.close()
            self.notification_conn = None 

    async def get_task_insight(self, task_id: str) -> Optional[CommunityInsight]:
        """Get insight by task_id."""
        logger.info(f"Getting insight for task {task_id}")
        try:
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            insight = result.scalar_one_or_none()
            
            if not insight:
                logger.error(f"No insight found for task_id: {task_id}")
                return None
                
            logger.info(f"Successfully retrieved insight for task {task_id}")
            return insight
        except Exception as e:
            logger.error(f"Error getting insight for task {task_id}: {str(e)}", exc_info=True)
            raise 