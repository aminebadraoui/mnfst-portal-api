from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings
from .routers import auth_router, auth, projects, ai, research_hub_router, advertorials_router
import logging

# Import all models to ensure they are registered with SQLAlchemy's metadata
from .models import *

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR, tags=["AI"])
app.include_router(research_hub_router, prefix=settings.API_V1_STR, tags=["Research Hub"])
app.include_router(advertorials_router, prefix=settings.API_V1_STR, tags=["Advertorials"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

logger.info("API started and routes configured")
