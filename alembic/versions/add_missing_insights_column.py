"""Add missing insights column

Revision ID: add_missing_insights_column
Revises: fix_analysis_tables
Create Date: 2024-01-09 05:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_missing_insights_column'
down_revision = 'fix_analysis_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add insights column to all analysis tables
    for table in ['avatar_analysis', 'pain_analysis', 'pattern_analysis', 'product_analysis', 'question_analysis']:
        op.add_column(table, sa.Column('insights', postgresql.JSON(), nullable=True, server_default='{}'))


def downgrade() -> None:
    # Remove insights column from all analysis tables
    for table in ['avatar_analysis', 'pain_analysis', 'pattern_analysis', 'product_analysis', 'question_analysis']:
        op.drop_column(table, 'insights') 