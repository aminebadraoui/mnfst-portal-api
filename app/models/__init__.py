"""
Models module initialization.
"""

from .base import Base
from .user import User
from .project import Project
from app.features.advertorials.models import StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial

# Import all models here to ensure they are registered with SQLAlchemy's metadata
__all__ = [
    'Base',
    'User',
    'Project',
    'StoryBasedAdvertorial',
    'ValueBasedAdvertorial',
    'InformationalAdvertorial',
]
