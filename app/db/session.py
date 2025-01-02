from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..core.config import settings

# Create async SQLAlchemy engine with the correct dialect options
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# Create sync engine for Celery tasks
sync_engine = create_engine(
    settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'),
    pool_pre_ping=True,
    echo=False,
    future=True
)

# Create async session maker for FastAPI
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create sync session maker for Celery tasks
SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_async_db():
    """Dependency to get async database session for FastAPI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """Get sync database session for Celery tasks."""
    session = SyncSessionLocal()
    try:
        return session
    finally:
        session.close() 