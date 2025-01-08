from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from uuid import UUID
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

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