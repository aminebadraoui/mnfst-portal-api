"""Fix analysis tables

Revision ID: fix_analysis_tables
Revises: 94d60e3ea6f7
Create Date: 2024-01-09 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_analysis_tables'
down_revision = '94d60e3ea6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing tables if they exist
    op.drop_table('avatar_analysis', if_exists=True)
    op.drop_table('pain_analysis', if_exists=True)
    op.drop_table('pattern_analysis', if_exists=True)
    op.drop_table('product_analysis', if_exists=True)
    op.drop_table('question_analysis', if_exists=True)

    # Create avatar_analysis table
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

    # Create pain_analysis table
    op.create_table(
        'pain_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='processing'),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='Pain & Frustration Analysis'),
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

    # Create pattern_analysis table
    op.create_table(
        'pattern_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='processing'),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='Pattern Detection'),
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

    # Create product_analysis table
    op.create_table(
        'product_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='processing'),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='Popular Products Analysis'),
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

    # Create question_analysis table
    op.create_table(
        'question_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='processing'),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='Question & Advice Mapping'),
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
    for table in ['avatar_analysis', 'pain_analysis', 'pattern_analysis', 'product_analysis', 'question_analysis']:
        op.create_index(f'ix_{table}_user_project', table, ['user_id', 'project_id'])
        op.create_index(f'ix_{table}_project_query', table, ['project_id', 'query'])
        op.create_index(f'ix_{table}_task_id', table, ['task_id'], unique=True)


def downgrade() -> None:
    # Drop all tables
    op.drop_table('avatar_analysis')
    op.drop_table('pain_analysis')
    op.drop_table('pattern_analysis')
    op.drop_table('product_analysis')
    op.drop_table('question_analysis') 