"""drop user project unique constraint

Revision ID: c215b58c974a
Revises: 9f5d7b30778b
Create Date: 2025-01-06 15:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c215b58c974a'
down_revision: Union[str, None] = '9f5d7b30778b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the unique index on user_id and project_id
    op.drop_index('ix_community_insights_user_project', table_name='community_insights')
    
    # Recreate the index without the unique constraint
    op.create_index('ix_community_insights_user_project', 'community_insights', ['user_id', 'project_id'], unique=False)


def downgrade() -> None:
    # Drop the non-unique index
    op.drop_index('ix_community_insights_user_project', table_name='community_insights')
    
    # Recreate the unique index
    op.create_index('ix_community_insights_user_project', 'community_insights', ['user_id', 'project_id'], unique=True) 