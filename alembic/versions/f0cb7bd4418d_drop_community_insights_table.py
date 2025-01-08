"""drop_community_insights_table

Revision ID: f0cb7bd4418d
Revises: de40ec485422
Create Date: 2024-01-08 02:24:30.911026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0cb7bd4418d'
down_revision: Union[str, None] = 'de40ec485422'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the community_insights table
    op.drop_table('community_insights')


def downgrade() -> None:
    # Recreate the community_insights table if needed to rollback
    op.create_table('community_insights',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('query', sa.String(), nullable=True),
        sa.Column('insights', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    ) 