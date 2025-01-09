from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import (
    StoryBasedAdvertorialRepository,
    ValueBasedAdvertorialRepository,
    InformationalAdvertorialRepository
)
from .ai_agents.generators import (
    story_based_agent,
    value_based_agent,
    informational_agent
)

logger = logging.getLogger(__name__)

async def generate_advertorials(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    description: str
) -> tuple[UUID, UUID, UUID]:
    """
    Generate all three types of advertorials in parallel and return their IDs
    """
    logger.info(f"Starting advertorial generation for project {project_id} by user {user_id}")
    logger.debug(f"Project description: {description}")

    # Create records for each type
    try:
        story_repo = StoryBasedAdvertorialRepository(db)
        value_repo = ValueBasedAdvertorialRepository(db)
        info_repo = InformationalAdvertorialRepository(db)

        story_ad = await story_repo.create(project_id, user_id)
        value_ad = await value_repo.create(project_id, user_id)
        info_ad = await info_repo.create(project_id, user_id)

        logger.info("Created initial records for all three advertorial types")

        # Generate content using AI agents
        logger.info("Starting AI generation")
        story_result = await story_based_agent.run(description)
        logger.info("Story-based advertorial generated")
        
        value_result = await value_based_agent.run(description)
        logger.info("Value-based advertorial generated")
        
        info_result = await informational_agent.run(description)
        logger.info("Informational advertorial generated")

        # Store the markdown content directly
        await story_repo.update_content(story_ad.id, {"content": story_result.data.content})
        await value_repo.update_content(value_ad.id, {"content": value_result.data.content})
        await info_repo.update_content(info_ad.id, {"content": info_result.data.content})
        logger.info("Updated all records with generated content")

        await db.commit()
        return story_ad.id, value_ad.id, info_ad.id

    except Exception as e:
        logger.error(f"Error during advertorial generation: {str(e)}", exc_info=True)
        await db.rollback()
        if 'story_ad' in locals():
            await story_repo.update_error(story_ad.id, str(e))
        if 'value_ad' in locals():
            await value_repo.update_error(value_ad.id, str(e))
        if 'info_ad' in locals():
            await info_repo.update_error(info_ad.id, str(e))
        await db.commit()
        raise 