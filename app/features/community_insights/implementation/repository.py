from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import json

from ....models.community_insight import CommunityInsight
from ....core.notifications import notify_insight_update, get_notification_connection

logger = logging.getLogger(__name__)

class CommunityInsightRepository:
    # Template sections as a class variable
    TEMPLATE_SECTIONS = [
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

    def __init__(self, session: AsyncSession):
        self.session = session
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
        sections: List[Dict[str, Any]] = None,
        avatars: List[Dict[str, Any]] = None,
        raw_response: str = ""
    ) -> CommunityInsight:
        """Create a new insight with initial empty sections."""
        logger.info(f"Creating insight for task {task_id}")
        
        # Initialize with template sections
        template_sections = [
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
            task_id=task_id,
            user_id=user_id,
            project_id=project_id,
            query=query,
            status="processing",
            sections=json.dumps(sections or template_sections),  # JSON serialize the initial sections
            avatars=json.dumps(avatars or []),  # JSON serialize the avatars too
            raw_perplexity_response=raw_response
        )
        
        self.session.add(insight)
        await self.session.commit()
        
        # Send notification if possible
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

    async def append_to_insight(
        self,
        task_id: str,
        new_sections: List[Dict[str, Any]] = None,
        new_avatars: List[Dict[str, Any]] = None,
        raw_response: str = None,
        error: str = None
    ) -> None:
        """Append new sections or avatars to an existing insight."""
        logger.info(f"[APPEND] Starting append_to_insight for task {task_id}")
        if new_sections:
            logger.info(f"[APPEND] Received new sections to append: {json.dumps(new_sections, indent=2)}")
        
        stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
        result = await self.session.execute(stmt)
        insight = result.scalar_one_or_none()
        
        if not insight:
            raise ValueError(f"No insight found for task_id: {task_id}")
        
        logger.info(f"[APPEND] Current insight sections: {insight.sections}")
        
        # Update sections - merge with existing sections
        if new_sections:
            try:
                # Ensure existing sections is a list
                existing_sections = []
                if insight.sections:
                    try:
                        if isinstance(insight.sections, str):
                            logger.info("[APPEND] Parsing sections from JSON string")
                            existing_sections = json.loads(insight.sections)
                        else:
                            logger.info("[APPEND] Using sections as list")
                            existing_sections = insight.sections
                    except json.JSONDecodeError:
                        logger.error("[APPEND] Failed to decode existing sections JSON, starting fresh")
                        existing_sections = []
                
                logger.info(f"[APPEND] Existing sections after parsing: {json.dumps(existing_sections, indent=2)}")
                
                # Create a map of existing sections
                section_map = {section["title"]: section for section in existing_sections}
                logger.info(f"[APPEND] Created section map with keys: {list(section_map.keys())}")
                
                # Process each new section
                for new_section in new_sections:
                    title = new_section["title"]
                    logger.info(f"[APPEND] Processing new section: {title}")
                    if title in section_map:
                        logger.info(f"[APPEND] Merging with existing section: {title}")
                        # Merge insights for existing section
                        existing_insights = section_map[title].get("insights", [])
                        new_insights = new_section.get("insights", [])
                        
                        logger.info(f"[APPEND] Existing insights count: {len(existing_insights)}")
                        logger.info(f"[APPEND] New insights count: {len(new_insights)}")
                        
                        # Create a set of existing insight titles for deduplication
                        existing_titles = {(insight.get("title", ""), insight.get("query", "")) for insight in existing_insights}
                        
                        # Only add new insights that don't exist yet
                        added_count = 0
                        for new_insight in new_insights:
                            key = (new_insight.get("title", ""), new_insight.get("query", ""))
                            if key not in existing_titles:
                                existing_insights.append(new_insight)
                                added_count += 1
                        
                        logger.info(f"[APPEND] Added {added_count} new insights to section {title}")
                        section_map[title]["insights"] = existing_insights
                    else:
                        logger.info(f"[APPEND] Adding new section: {title}")
                        # Add new section
                        section_map[title] = new_section
                
                # Convert to list and ensure it's JSON serializable
                sections_list = list(section_map.values())
                logger.info(f"[APPEND] Final sections list: {json.dumps(sections_list, indent=2)}")
                
                # Update the insight with merged sections
                insight.sections = json.dumps(sections_list)  # Explicitly serialize to JSON string
                await self.session.commit()
                logger.info(f"[APPEND] Committed changes to database for section {title}")
                
                # Verify the update
                stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
                result = await self.session.execute(stmt)
                updated_insight = result.scalar_one_or_none()
                if updated_insight and updated_insight.sections:
                    try:
                        sections = json.loads(updated_insight.sections) if isinstance(updated_insight.sections, str) else updated_insight.sections
                        logger.info(f"[APPEND] Verification - Retrieved sections: {json.dumps(sections, indent=2)}")
                        for section in sections:
                            if section["title"] == title:
                                logger.info(f"[APPEND] Verified section {title} has {len(section.get('insights', []))} insights after save")
                    except Exception as e:
                        logger.error(f"[APPEND] Error verifying section update: {str(e)}", exc_info=True)
                
            except Exception as e:
                logger.error(f"[APPEND] Error updating sections: {str(e)}", exc_info=True)
                raise
        
        # Update avatars - store as is without merging
        if new_avatars:
            try:
                insight.avatars = json.dumps(new_avatars)
                await self.session.commit()
                logger.info(f"Avatars section updated and saved to database with {len(new_avatars)} avatars")
            except Exception as e:
                logger.error(f"Error updating avatars: {str(e)}", exc_info=True)
                raise
            
        # Update raw response - store as is
        if raw_response:
            try:
                insight.raw_perplexity_response = raw_response
                await self.session.commit()
                logger.info("Raw response updated and saved to database")
            except Exception as e:
                logger.error(f"Error updating raw response: {str(e)}", exc_info=True)
                raise
        
        # Update error if provided
        if error:
            try:
                insight.error = error
                insight.status = "error"
                await self.session.commit()
                logger.info(f"Error status updated and saved to database: {error}")
            except Exception as e:
                logger.error(f"Error updating error status: {str(e)}", exc_info=True)
                raise
        
        # Send notification if possible
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
        
        logger.info(f"Successfully updated insight for task {task_id} with status {insight.status}")

    async def get_project_queries(self, project_id: str) -> List[str]:
        """Get all unique queries for a project's insights."""
        stmt = select(CommunityInsight.query).where(
            and_(
                CommunityInsight.project_id == project_id,
                CommunityInsight.query.isnot(None)
            )
        ).distinct()
        
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_project_insights(
        self,
        project_id: str,
        query: str = None,
        task_id: str = None
    ) -> Dict[str, Any]:
        """Get insights either by task ID or combined for a project."""
        logger.info(f"[GET] Getting insights - project: {project_id}, task: {task_id}, query: {query}")
        
        if task_id:
            # Case 1: Get specific insight by task_id (for polling)
            stmt = select(CommunityInsight).where(CommunityInsight.task_id == task_id)
            result = await self.session.execute(stmt)
            insight = result.scalar_one_or_none()
            
            if insight:
                logger.info(f"[GET] Found insight with status: {insight.status}")
                try:
                    sections = json.loads(insight.sections) if isinstance(insight.sections, str) else insight.sections
                    avatars = json.loads(insight.avatars) if isinstance(insight.avatars, str) else insight.avatars
                    
                    return {
                        "status": insight.status,
                        "sections": sections or [],
                        "avatars": avatars or [],
                        "error": insight.error,
                        "raw_perplexity_response": insight.raw_perplexity_response
                    }
                except Exception as e:
                    logger.error(f"[GET] Error parsing insight data: {str(e)}")
                    return {
                        "status": insight.status,
                        "sections": insight.sections or [],
                        "avatars": insight.avatars or [],
                        "error": insight.error,
                        "raw_perplexity_response": insight.raw_perplexity_response
                    }
        else:
            # Case 2: Get all insights for project (for initial load)
            stmt = select(CommunityInsight).where(CommunityInsight.project_id == project_id)
            if query:
                stmt = stmt.where(CommunityInsight.query == query)
            result = await self.session.execute(stmt)
            insights = result.scalars().all()
            
            if not insights:
                return {
                    "status": "completed",
                    "sections": [],
                    "avatars": [],
                    "error": None,
                    "raw_perplexity_response": None
                }
            
            # Get overall status (processing if any insight is processing)
            status = "processing" if any(i.status == "processing" for i in insights) else "completed"
            error = next((i.error for i in insights if i.error), None)
            
            # Combine sections from all insights
            all_sections = []
            section_map = {}
            raw_responses = []
            all_avatars = []
            
            for insight in insights:
                try:
                    if insight.sections:
                        sections = json.loads(insight.sections) if isinstance(insight.sections, str) else insight.sections
                        for section in sections:
                            title = section.get("title")
                            if title not in section_map:
                                section_map[title] = {
                                    "title": title,
                                    "icon": section.get("icon", ""),
                                    "insights": []
                                }
                            section_map[title]["insights"].extend(section.get("insights", []))
                    
                    if insight.avatars:
                        avatars = json.loads(insight.avatars) if isinstance(insight.avatars, str) else insight.avatars
                        all_avatars.extend(avatars or [])
                    
                    if insight.raw_perplexity_response:
                        raw_responses.append(insight.raw_perplexity_response)
                except Exception as e:
                    logger.error(f"[GET] Error processing insight {insight.task_id}: {str(e)}")
                    continue
            
            # Convert section map to list and deduplicate insights
            for section in section_map.values():
                unique_insights = {}
                for insight in section["insights"]:
                    key = (insight.get("title", ""), insight.get("query", ""))
                    if key not in unique_insights:
                        unique_insights[key] = insight
                section["insights"] = list(unique_insights.values())
                all_sections.append(section)
            
            return {
                "status": status,
                "sections": all_sections,
                "avatars": all_avatars,
                "error": error,
                "raw_perplexity_response": "\n\n".join(raw_responses) if raw_responses else None
            }
        
        # Return empty state if no insight found
        return {
            "status": "processing",
            "sections": [],
            "avatars": [],
            "error": None,
            "raw_perplexity_response": None
        } 