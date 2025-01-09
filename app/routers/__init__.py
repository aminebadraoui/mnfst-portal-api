from fastapi import APIRouter
from .auth import router as auth_router
from .projects import router as projects_router
from .ai import router as ai_router
from .research_hub import router as research_hub_router
from ..features.advertorials.router import router as advertorials_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(ai_router)
router.include_router(research_hub_router)
router.include_router(advertorials_router)

__all__ = [
    "auth_router",
    "projects_router",
    "ai_router",
    "research_hub_router",
    "advertorials_router",
    "router"
]
