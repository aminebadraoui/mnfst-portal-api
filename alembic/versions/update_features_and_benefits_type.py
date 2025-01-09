"""update features_and_benefits type

Revision ID: update_features_and_benefits_type
Revises: add_product_id_to_advertorials
Create Date: 2024-01-09 04:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_features_and_benefits_type'
down_revision = 'add_product_id_to_advertorials'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Convert existing text data to JSONB
    op.execute("""
        ALTER TABLE products 
        ALTER COLUMN features_and_benefits TYPE JSONB 
        USING features_and_benefits::jsonb
    """)

def downgrade() -> None:
    # Convert JSONB back to text
    op.execute("""
        ALTER TABLE products 
        ALTER COLUMN features_and_benefits TYPE TEXT 
        USING features_and_benefits::text
    """) 