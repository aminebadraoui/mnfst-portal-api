"""add community insights table

Revision ID: b9718636889c
Revises: f1234567890a
Create Date: 2025-01-06 02:36:32.467555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b9718636889c'
down_revision: Union[str, None] = 'f1234567890a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create community_insights table
    op.create_table(
        'community_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('sections', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('avatars', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('raw_perplexity_response', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_community_insights_task_id', 'community_insights', ['task_id'])
    op.create_index('ix_community_insights_user_project', 'community_insights', ['user_id', 'project_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_community_insights_user_project')
    op.drop_index('ix_community_insights_task_id')
    
    # Drop the table
    op.drop_table('community_insights') 