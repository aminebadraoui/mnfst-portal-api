"""recreate_all_tables

Revision ID: eaed97c76bb6
Revises: 78e8b04e2814
Create Date: 2025-01-08 16:15:45.978384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eaed97c76bb6'
down_revision: Union[str, None] = '78e8b04e2814'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), unique=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create story_based_advertorials table
    op.create_table(
        'story_based_advertorials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('error', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_story_based_advertorials_project_id', 'story_based_advertorials', ['project_id'])
    op.create_index('ix_story_based_advertorials_user_id', 'story_based_advertorials', ['user_id'])

    # Create value_based_advertorials table
    op.create_table(
        'value_based_advertorials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('error', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_value_based_advertorials_project_id', 'value_based_advertorials', ['project_id'])
    op.create_index('ix_value_based_advertorials_user_id', 'value_based_advertorials', ['user_id'])

    # Create informational_advertorials table
    op.create_table(
        'informational_advertorials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('error', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_informational_advertorials_project_id', 'informational_advertorials', ['project_id'])
    op.create_index('ix_informational_advertorials_user_id', 'informational_advertorials', ['user_id'])


def downgrade() -> None:
    op.drop_table('informational_advertorials')
    op.drop_table('value_based_advertorials')
    op.drop_table('story_based_advertorials')
    op.drop_table('projects')
    op.drop_table('users') 