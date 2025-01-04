from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True 