from fastapi import APIRouter, Depends
from app.features.products.routes import router as products_feature_router
from app.core.auth import get_current_user

router = APIRouter()
router.include_router(products_feature_router) 