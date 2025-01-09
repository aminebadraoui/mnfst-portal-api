"""restore all tables

Revision ID: restore_all_tables
Revises: None
Create Date: 2025-01-08 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'restore_all_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute('DROP SCHEMA public CASCADE')
    op.execute('CREATE SCHEMA public')
    
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
        'avatar_analysis',
        'pain_analysis',
        'pattern_analysis',
        'product_analysis',
        'question_analysis'
    ]

    for table_name in analysis_tables:
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
        'story_based_advertorials',
        'value_based_advertorials',
        'informational_advertorials'
    ]

    for table_name in advertorial_tables:
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
    op.execute('DROP SCHEMA public CASCADE')
    op.execute('CREATE SCHEMA public') 