"""create products table

Revision ID: create_products_table
Revises: None
Create Date: 2024-01-09 04:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_products_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create products table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT NOT NULL,
            features_and_benefits TEXT NOT NULL,
            guarantee TEXT,
            price NUMERIC(10, 2),
            is_service BOOLEAN DEFAULT FALSE,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index if it doesn't exist
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_products_project_id ON products (project_id)
    """)

def downgrade() -> None:
    # Drop products table if it exists
    op.execute("""
        DROP TABLE IF EXISTS products CASCADE
    """) 