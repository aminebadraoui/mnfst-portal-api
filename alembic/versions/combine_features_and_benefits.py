"""combine features and benefits

Revision ID: combine_features_and_benefits
Revises: create_all_tables
Create Date: 2024-01-09 02:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'combine_features_and_benefits'
down_revision = 'create_all_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add new column
    op.add_column('products', sa.Column('features_and_benefits', sa.Text))
    
    # Copy data from old columns (if table exists)
    op.execute("""
        UPDATE products 
        SET features_and_benefits = features || benefits 
        WHERE features IS NOT NULL AND benefits IS NOT NULL
    """)
    
    # Make the new column not nullable
    op.alter_column('products', 'features_and_benefits', nullable=False)
    
    # Drop old columns
    op.drop_column('products', 'features')
    op.drop_column('products', 'benefits')

def downgrade() -> None:
    # Add back old columns
    op.add_column('products', sa.Column('features', sa.Text))
    op.add_column('products', sa.Column('benefits', sa.Text))
    
    # Copy data back (if any)
    op.execute("""
        UPDATE products 
        SET 
            features = features_and_benefits,
            benefits = features_and_benefits
        WHERE features_and_benefits IS NOT NULL
    """)
    
    # Make old columns not nullable
    op.alter_column('products', 'features', nullable=False)
    op.alter_column('products', 'benefits', nullable=False)
    
    # Drop new column
    op.drop_column('products', 'features_and_benefits') 