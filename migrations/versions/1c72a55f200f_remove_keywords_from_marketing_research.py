"""remove_keywords_from_marketing_research

Revision ID: 1c72a55f200f
Revises: 0ae1a1309977
Create Date: 2025-01-01 00:58:30.817533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c72a55f200f'
down_revision: Union[str, None] = '0ae1a1309977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the keywords column
    op.drop_column('marketing_research', 'keywords')


def downgrade() -> None:
    # Add the keywords column back
    op.add_column('marketing_research',
        sa.Column('keywords', sa.ARRAY(sa.String()), server_default='{}', nullable=True)
    )
