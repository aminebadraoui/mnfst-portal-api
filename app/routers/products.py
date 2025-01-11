from fastapi import APIRouter, Depends
from app.features.products.router import router as products_feature_router
from app.core.auth import get_current_user

router = products_feature_router 