import os
import sys
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.features.research_hub.models.database.pain_analysis import PainAnalysis
from app.features.research_hub.models.database.question_analysis import QuestionAnalysis
from app.features.research_hub.models.database.pattern_analysis import PatternAnalysis
from app.features.research_hub.models.database.product_analysis import ProductAnalysis
from app.features.research_hub.models.database.avatar_analysis import AvatarAnalysis
from app.features.advertorials.models import StoryBasedAdvertorial, ValueBasedAdvertorial, InformationalAdvertorial

# Register all models
models = [
    User,
    Project,
    PainAnalysis,
    QuestionAnalysis,
    PatternAnalysis,
    ProductAnalysis,
    AvatarAnalysis,
    StoryBasedAdvertorial,
    ValueBasedAdvertorial,
    InformationalAdvertorial
]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    url = settings.DATABASE_URL
    # Convert async URL to sync URL for Alembic
    return url.replace("+asyncpg", "")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations()) 