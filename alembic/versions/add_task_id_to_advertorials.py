"""add task_id to advertorials

Revision ID: add_task_id_to_advertorials
Revises: 64391b4abf8b
Create Date: 2025-01-08 16:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'add_task_id_to_advertorials'
down_revision = '64391b4abf8b'
branch_labels = None
depends_on = None

def upgrade():
    # Add task_id column to story_based_advertorials
    op.add_column('story_based_advertorials', sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_story_based_advertorials_task_id', 'story_based_advertorials', ['task_id'], unique=True)
    
    # Add task_id column to value_based_advertorials
    op.add_column('value_based_advertorials', sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_value_based_advertorials_task_id', 'value_based_advertorials', ['task_id'], unique=True)
    
    # Add task_id column to informational_advertorials
    op.add_column('informational_advertorials', sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_informational_advertorials_task_id', 'informational_advertorials', ['task_id'], unique=True)
    
    # Generate unique task_ids for existing rows
    connection = op.get_bind()
    
    # Update story_based_advertorials
    story_based = sa.Table(
        'story_based_advertorials',
        sa.MetaData(),
        sa.Column('id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_id', postgresql.UUID(as_uuid=True))
    )
    for row in connection.execute(story_based.select()):
        connection.execute(
            story_based.update().where(
                story_based.c.id == row.id
            ).values(
                task_id=uuid.uuid4()
            )
        )
    
    # Update value_based_advertorials
    value_based = sa.Table(
        'value_based_advertorials',
        sa.MetaData(),
        sa.Column('id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_id', postgresql.UUID(as_uuid=True))
    )
    for row in connection.execute(value_based.select()):
        connection.execute(
            value_based.update().where(
                value_based.c.id == row.id
            ).values(
                task_id=uuid.uuid4()
            )
        )
    
    # Update informational_advertorials
    informational = sa.Table(
        'informational_advertorials',
        sa.MetaData(),
        sa.Column('id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_id', postgresql.UUID(as_uuid=True))
    )
    for row in connection.execute(informational.select()):
        connection.execute(
            informational.update().where(
                informational.c.id == row.id
            ).values(
                task_id=uuid.uuid4()
            )
        )
    
    # Make task_id not nullable
    op.alter_column('story_based_advertorials', 'task_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
    op.alter_column('value_based_advertorials', 'task_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
    op.alter_column('informational_advertorials', 'task_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)

def downgrade():
    # Drop task_id column from story_based_advertorials
    op.drop_index('ix_story_based_advertorials_task_id', table_name='story_based_advertorials')
    op.drop_column('story_based_advertorials', 'task_id')
    
    # Drop task_id column from value_based_advertorials
    op.drop_index('ix_value_based_advertorials_task_id', table_name='value_based_advertorials')
    op.drop_column('value_based_advertorials', 'task_id')
    
    # Drop task_id column from informational_advertorials
    op.drop_index('ix_informational_advertorials_task_id', table_name='informational_advertorials')
    op.drop_column('informational_advertorials', 'task_id') 