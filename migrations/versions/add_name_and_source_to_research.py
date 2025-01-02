"""add_name_and_source_to_research

Revision ID: add_name_and_source
Revises: 1c72a55f200f
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_name_and_source'
down_revision: Union[str, None] = '1c72a55f200f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add name and source columns with temporary nullable=True
    op.add_column('marketing_research', sa.Column('name', sa.String(), nullable=True))
    op.add_column('marketing_research', sa.Column('source', sa.String(), nullable=True))
    
    # Update existing rows with default values
    op.execute("UPDATE marketing_research SET name = 'Untitled Research', source = 'reddit' WHERE name IS NULL")
    
    # Make columns non-nullable
    op.alter_column('marketing_research', 'name', nullable=False)
    op.alter_column('marketing_research', 'source', nullable=False)


def downgrade() -> None:
    op.drop_column('marketing_research', 'name')
    op.drop_column('marketing_research', 'source') 