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
from .ai_agents.dependencies import (
    StoryAdvertorialDeps,
    ValueAdvertorialDeps,
    InformationalAdvertorialDeps
)

logger = logging.getLogger(__name__)

async def generate_advertorials(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    project_description: str,
    product_description: str,
    product_id: UUID
) -> tuple[UUID, UUID, UUID]:
    """
    Generate all three types of advertorials in parallel and return their IDs
    """
    logger.info(f"Starting advertorial generation for project {project_id} by user {user_id}")
    logger.debug(f"Project description: {project_description}")
    logger.debug(f"Product description: {product_description}")

    story_repo = StoryBasedAdvertorialRepository(db)
    value_repo = ValueBasedAdvertorialRepository(db)
    info_repo = InformationalAdvertorialRepository(db)

    try:
        # Create initial records
        story_ad = await story_repo.create(project_id, user_id, product_id)
        value_ad = await value_repo.create(project_id, user_id, product_id)
        info_ad = await info_repo.create(project_id, user_id, product_id)
        await db.commit()  # Commit the initial records

        logger.info("Created initial records for all three advertorial types")

        try:
            # Generate content using AI agents
            logger.info("Starting AI generation")
            
            # Create dependencies objects with string values
            story_deps = StoryAdvertorialDeps(
                project_description=str(project_description),
                product_description=str(product_description)
            )
            value_deps = ValueAdvertorialDeps(
                project_description=str(project_description),
                product_description=str(product_description)
            )
            info_deps = InformationalAdvertorialDeps(
                project_description=str(project_description),
                product_description=str(product_description)
            )
            
            # Run agents with dependencies and user prompts
            story_result = await story_based_agent.run(
                "Generate a story-based advertorial using the provided project and product descriptions.",
                deps=story_deps
            )
            logger.info("Story-based advertorial generated")
            
            value_result = await value_based_agent.run(
                "Generate a value-based advertorial using the provided project and product descriptions.",
                deps=value_deps
            )
            logger.info("Value-based advertorial generated")
            
            info_result = await informational_agent.run(
                "Generate an informational advertorial using the provided project and product descriptions.",
                deps=info_deps
            )
            logger.info("Informational advertorial generated")

            # Store the markdown content directly
            await story_repo.update_content(story_ad.id, {"content": story_result.data.content})
            await value_repo.update_content(value_ad.id, {"content": value_result.data.content})
            await info_repo.update_content(info_ad.id, {"content": info_result.data.content})
            logger.info("Updated all records with generated content")

            await db.commit()
            return story_ad.id, value_ad.id, info_ad.id

        except Exception as e:
            logger.error(f"Error during content generation: {str(e)}", exc_info=True)
            # Since the initial records were committed, we can safely update their error status
            await story_repo.update_error(story_ad.id, str(e))
            await value_repo.update_error(value_ad.id, str(e))
            await info_repo.update_error(info_ad.id, str(e))
            await db.commit()
            raise

    except Exception as e:
        logger.error(f"Error during advertorial creation: {str(e)}", exc_info=True)
        await db.rollback()
        raise 