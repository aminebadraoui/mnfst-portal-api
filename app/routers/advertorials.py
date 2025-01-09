from fastapi import APIRouter, Depends, HTTPException
import asyncio
from ..models.user import User
from .auth import JWTBearer
from ..models.project import Project
from ..features.advertorials.models import AdvertorialRequest, AdvertorialSet
from ..features.advertorials.dependencies import ProjectContext
from ..features.advertorials.generators import (
    story_based_agent,
    informational_agent,
    value_based_agent
)

router = APIRouter(
    prefix="/projects/{project_id}/advertorials",
    tags=["advertorials"],
    dependencies=[Depends(JWTBearer())]
)

@router.post("/generate", response_model=AdvertorialSet)
async def generate_advertorials(
    project_id: str,
    request: AdvertorialRequest,
    current_user: User = Depends(JWTBearer()),
    project: Project = Depends(Project.get_by_id)
):
    try:
        # Create project context
        project_context = ProjectContext(
            title=project.title,
            description=project.description
        )

        # Generate advertorials in parallel
        results = await asyncio.gather(
            story_based_agent.run(request, deps=project_context),
            informational_agent.run(request, deps=project_context),
            value_based_agent.run(request, deps=project_context)
        )

        # Convert results to AdvertorialSet
        return AdvertorialSet(
            story_based=results[0].data,
            informational=results[1].data,
            value_based=results[2].data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 