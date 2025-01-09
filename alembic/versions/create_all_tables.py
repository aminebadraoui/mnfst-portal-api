"""create all tables

Revision ID: create_all_tables
Revises: None
Create Date: 2025-01-08 16:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'create_all_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('first_name', sa.String, nullable=True),
        sa.Column('last_name', sa.String, nullable=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'))
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # Create analysis tables
    analysis_tables = [
        ('avatar_analysis', 'Avatar Analysis'),
        ('pain_analysis', 'Pain Analysis'),
        ('pattern_analysis', 'Pattern Analysis'),
        ('product_analysis', 'Product Analysis'),
        ('question_analysis', 'Question Analysis')
    ]

    for table_name, _ in analysis_tables:
        op.create_table(
            table_name,
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('content', postgresql.JSONB, nullable=True),
            sa.Column('status', sa.String, nullable=False),
            sa.Column('error', sa.String, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )
        op.create_index(f'ix_{table_name}_project_id', table_name, ['project_id'])
        op.create_index(f'ix_{table_name}_user_id', table_name, ['user_id'])

    # Create advertorial tables
    advertorial_tables = [
        ('story_based_advertorials', 'Story Based Advertorials'),
        ('value_based_advertorials', 'Value Based Advertorials'),
        ('informational_advertorials', 'Informational Advertorials')
    ]

    for table_name, _ in advertorial_tables:
        op.create_table(
            table_name,
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('content', postgresql.JSONB, nullable=True),
            sa.Column('status', sa.String, nullable=False),
            sa.Column('error', sa.String, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )
        op.create_index(f'ix_{table_name}_project_id', table_name, ['project_id'])
        op.create_index(f'ix_{table_name}_user_id', table_name, ['user_id'])
        op.create_index(f'ix_{table_name}_task_id', table_name, ['task_id'], unique=True)

def downgrade() -> None:
    # Drop advertorial tables
    op.drop_table('story_based_advertorials')
    op.drop_table('value_based_advertorials')
    op.drop_table('informational_advertorials')

    # Drop analysis tables
    op.drop_table('avatar_analysis')
    op.drop_table('pain_analysis')
    op.drop_table('pattern_analysis')
    op.drop_table('product_analysis')
    op.drop_table('question_analysis')

    # Drop projects table
    op.drop_table('projects')

    # Drop users table
    op.drop_table('users') 