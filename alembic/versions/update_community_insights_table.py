"""update community insights table for one-to-one relationship

Revision ID: c9876543210b
Revises: b9718636889c
Create Date: 2025-01-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c9876543210b'
down_revision: Union[str, None] = 'b9718636889c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing indexes
    op.drop_index('ix_community_insights_task_id')
    op.drop_index('ix_community_insights_user_project')

    # Create a temporary table to store the latest insight for each project
    op.execute("""
        CREATE TEMP TABLE latest_insights AS
        SELECT DISTINCT ON (project_id) *
        FROM community_insights
        ORDER BY project_id, created_at DESC
    """)

    # Delete all insights from the main table
    op.execute("DELETE FROM community_insights")

    # Copy back only the latest insights
    op.execute("""
        INSERT INTO community_insights
        SELECT * FROM latest_insights
    """)

    # Drop the temporary table
    op.execute("DROP TABLE latest_insights")

    # Drop task_id column
    op.drop_column('community_insights', 'task_id')
    
    # Add query column
    op.add_column('community_insights', sa.Column('query', sa.String(), nullable=True))

    # Update status column default
    op.alter_column('community_insights', 'status',
                    existing_type=sa.String(),
                    server_default=sa.text("'completed'"),
                    existing_nullable=False)

    # Create a composite index on project_id and query
    op.create_index('ix_community_insights_project_query', 'community_insights', ['project_id', 'query'])


def downgrade() -> None:
    # Drop new index
    op.drop_index('ix_community_insights_project_query')
    
    # Drop query column
    op.drop_column('community_insights', 'query')

    # Add back task_id column
    op.add_column('community_insights',
                  sa.Column('task_id', sa.String(), nullable=False))

    # Remove status default
    op.alter_column('community_insights', 'status',
                    existing_type=sa.String(),
                    server_default=None,
                    existing_nullable=False)

    # Recreate original indexes
    op.create_index('ix_community_insights_task_id', 'community_insights', ['task_id'])
    op.create_index('ix_community_insights_user_project', 'community_insights', ['user_id', 'project_id'], unique=False) 