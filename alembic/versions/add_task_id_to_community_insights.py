"""add task_id to community insights

Revision ID: add_task_id
Revises: c215b58c974a
Create Date: 2024-01-06 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'add_task_id'
down_revision = 'c215b58c974a'
branch_labels = None
depends_on = None

def upgrade():
    # Add task_id column
    op.add_column('community_insights', sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generate unique task_ids for existing rows
    connection = op.get_bind()
    community_insights = sa.Table(
        'community_insights',
        sa.MetaData(),
        sa.Column('id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_id', postgresql.UUID(as_uuid=True))
    )
    
    for row in connection.execute(community_insights.select()):
        connection.execute(
            community_insights.update().where(
                community_insights.c.id == row.id
            ).values(
                task_id=uuid.uuid4()
            )
        )
    
    # Make task_id not nullable and add index
    op.alter_column('community_insights', 'task_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
    op.create_index('ix_community_insights_task_id', 'community_insights', ['task_id'], unique=True)

def downgrade():
    op.drop_index('ix_community_insights_task_id', table_name='community_insights')
    op.drop_column('community_insights', 'task_id') 