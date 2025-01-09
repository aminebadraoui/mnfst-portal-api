from fastapi import APIRouter
from app.features.advertorials.router import router as advertorials_feature_router

router = APIRouter()
router.include_router(advertorials_feature_router) 