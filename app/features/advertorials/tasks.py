from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import get_db
from .repository import AdvertorialRepository
from .generators import generate_advertorials
from .models import AdvertorialRequest

@shared_task(bind=True)
async def generate_advertorials_task(
    self,
    advertorial_id: str,
    project_description: str,
    request_data: dict
):
    """Celery task to generate advertorials in the background."""
    try:
        # Get database session
        db: Session = next(get_db())
        repo = AdvertorialRepository(db)

        # Convert dict to AdvertorialRequest
        request = AdvertorialRequest(**request_data)

        # Generate advertorials
        story, info, value = await generate_advertorials(
            project_description=project_description,
            request=request
        )

        # Update the advertorial record with results
        await repo.update_content(
            id=advertorial_id,
            story_based=story,
            informational=info,
            value_based=value
        )

    except Exception as e:
        # Update status to failed with error message
        await repo.update_status(
            id=advertorial_id,
            status="failed",
            error=str(e)
        )
        raise  # Re-raise the exception for Celery to handle 