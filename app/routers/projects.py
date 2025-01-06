from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from ..models.project import Project
from ..core.deps import get_current_user, get_db
from ..models.user import User
from ..features.community_insights.implementation.service import CommunityInsightsService
from ..features.community_insights.implementation.models import CommunityInsightsResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_project = Project(**project.model_dump(), user_id=current_user.id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        Project.__table__.select().where(Project.user_id == current_user.id)
    )
    return query.all()

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        Project.__table__.select()
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    project = query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        Project.__table__.select()
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    project = query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = project_update.model_dump(exclude_unset=True)
    await db.execute(
        Project.__table__.update()
        .where(Project.id == project_id)
        .values(**update_data)
    )
    await db.commit()
    
    # Fetch the updated project
    query = await db.execute(
        Project.__table__.select()
        .where(Project.id == project_id)
    )
    return query.first()

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        Project.__table__.select()
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    project = query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.execute(
        Project.__table__.delete().where(Project.id == project_id)
    )
    await db.commit()
    return None 

@router.get("/{project_id}/community-insight", response_model=CommunityInsightsResponse)
async def get_project_community_insight(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get community insights for a project."""
    service = CommunityInsightsService(db)
    try:
        insights = service.get_project_insights(project_id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{project_id}/community-insight", response_model=CommunityInsightsResponse)
async def generate_project_community_insight(
    project_id: str,
    topic_keyword: str,
    user_query: str,
    user_id: str,
    source_urls: Optional[List[str]] = None,
    product_urls: Optional[List[str]] = None,
    use_only_specified_sources: bool = False,
    db: Session = Depends(get_db)
):
    """Generate community insights for a project."""
    service = CommunityInsightsService(db)
    try:
        insights = service.process_insights(
            project_id=project_id,
            topic_keyword=topic_keyword,
            user_query=user_query,
            user_id=user_id,
            source_urls=source_urls or [],
            product_urls=product_urls or [],
            use_only_specified_sources=use_only_specified_sources
        )
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 