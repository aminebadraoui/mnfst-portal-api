"""Fix insights column

Revision ID: fix_insights_column
Revises: add_missing_insights_column
Create Date: 2024-01-09 05:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_insights_column'
down_revision = 'add_missing_insights_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop and recreate avatar_analysis table
    op.drop_table('avatar_analysis')
    op.create_table(
        'avatar_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='processing'),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='Avatars'),
        sa.Column('query', sa.String(), nullable=True),
        sa.Column('insights', postgresql.JSON(), nullable=True, server_default='{}'),
        sa.Column('raw_perplexity_response', sa.String(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('ix_avatar_analysis_user_project', 'avatar_analysis', ['user_id', 'project_id'])
    op.create_index('ix_avatar_analysis_project_query', 'avatar_analysis', ['project_id', 'query'])
    op.create_index('ix_avatar_analysis_task_id', 'avatar_analysis', ['task_id'], unique=True)


def downgrade() -> None:
    op.drop_table('avatar_analysis') 