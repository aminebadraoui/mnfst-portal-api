"""add product_id to advertorials

Revision ID: add_product_id_to_advertorials
Revises: combine_features_and_benefits
Create Date: 2024-01-09 03:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_product_id_to_advertorials'
down_revision = 'combine_features_and_benefits'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add product_id to value_based_advertorials
    op.add_column('value_based_advertorials', 
                  sa.Column('product_id', postgresql.UUID(as_uuid=True), 
                           sa.ForeignKey('products.id'),
                           nullable=True))
    
    # Add index for faster lookups
    op.create_index('ix_value_based_advertorials_product_id',
                    'value_based_advertorials',
                    ['product_id'])
    
    # Add product_id to informational_advertorials
    op.add_column('informational_advertorials',
                  sa.Column('product_id', postgresql.UUID(as_uuid=True),
                           sa.ForeignKey('products.id'),
                           nullable=True))
    
    # Add index for faster lookups
    op.create_index('ix_informational_advertorials_product_id',
                    'informational_advertorials',
                    ['product_id'])

def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_value_based_advertorials_product_id')
    op.drop_index('ix_informational_advertorials_product_id')
    
    # Remove columns
    op.drop_column('value_based_advertorials', 'product_id')
    op.drop_column('informational_advertorials', 'product_id') 