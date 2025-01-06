"""add query column to community insights

Revision ID: 9f5d7b30778b
Revises: c9876543210b
Create Date: 2025-01-06 15:00:31.580557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9f5d7b30778b'
down_revision: Union[str, None] = 'c9876543210b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add query column
    op.add_column('community_insights', sa.Column('query', sa.String(), nullable=True))
    
    # Drop the unique constraint on project_id
    op.drop_constraint('uq_community_insights_project_id', 'community_insights', type_='unique')
    
    # Create a composite index on project_id and query
    op.create_index('ix_community_insights_project_query', 'community_insights', ['project_id', 'query'])


def downgrade() -> None:
    # Drop the composite index
    op.drop_index('ix_community_insights_project_query', table_name='community_insights')
    
    # Recreate the unique constraint on project_id
    op.create_unique_constraint('uq_community_insights_project_id', 'community_insights', ['project_id'])
    
    # Drop the query column
    op.drop_column('community_insights', 'query') 