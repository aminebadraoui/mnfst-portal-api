from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import setup_logging
from .routers import auth_router, projects, ai, research_hub_router, advertorials_router, products_router

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(research_hub_router, prefix="/api/v1")
app.include_router(advertorials_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
