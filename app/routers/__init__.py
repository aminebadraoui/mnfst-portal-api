from fastapi import APIRouter
from .auth import router as auth_router
from . import auth, projects, ai
from .research_hub import router as research_hub_router
from .advertorials import router as advertorials_router
from .products import router as products_router

__all__ = [
    'auth_router',
    'auth',
    'projects',
    'ai',
    'research_hub_router',
    'advertorials_router',
    'products_router'
]
